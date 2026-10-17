"""
InternIQ Development Launcher
Starts both the FastAPI/Uvicorn backend and Vite React frontend concurrently.

Usage:
    python run_dev.py                # Run both in the same terminal (unified logs)
    python run_dev.py --separate     # Run in separate terminal windows (Windows)
    python run_dev.py --kill-existing # Free ports 8000/5173 if already in use
"""

import argparse
import os
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

# Reconfigure stdout/stderr to UTF-8 on Windows to prevent UnicodeEncodeError
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Enable ANSI colors in Windows cmd
if sys.platform == "win32":
    os.system("")

COLOR_RESET = "\033[0m"
COLOR_CYAN = "\033[36m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_RED = "\033[31m"
COLOR_BOLD = "\033[1m"
COLOR_DIM = "\033[2m"

ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "frontend"


def get_python_executable() -> str:
    """Find the best Python executable (checks local venvs first)."""
    candidates = [
        ROOT_DIR / "scraperenv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python"),
        ROOT_DIR / ".venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python"),
        ROOT_DIR / "venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python"),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return sys.executable


def get_npm_executable() -> str:
    """Find npm executable on the system."""
    if sys.platform == "win32":
        npm = shutil.which("npm.cmd") or shutil.which("npm")
    else:
        npm = shutil.which("npm")
    if not npm:
        raise FileNotFoundError("Could not find 'npm' in PATH. Please install Node.js.")
    return npm


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a TCP port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex((host, port)) == 0


def get_pid_using_port(port: int) -> int | None:
    """Find the PID listening on a given port on Windows."""
    if sys.platform != "win32":
        return None
    try:
        output = subprocess.check_output("netstat -ano -p tcp", shell=True, text=True)
        for line in output.splitlines():
            parts = line.strip().split()
            if len(parts) >= 5 and parts[0].upper() == "TCP":
                local_addr = parts[1]
                state = parts[3].upper()
                pid = parts[4]
                if local_addr.endswith(f":{port}") and state in ("LISTENING", "ESTABLISHED") and pid != "0":
                    return int(pid)
    except Exception:
        pass
    return None


def kill_process_tree(pid: int) -> bool:
    """Forcefully terminate a process and its child processes."""
    if not pid:
        return False
    if sys.platform == "win32":
        res = subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return res.returncode == 0
    else:
        try:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
            return True
        except Exception:
            return False


def terminate_proc(proc: subprocess.Popen | None):
    """Safely terminate a subprocess.Popen instance and all child processes."""
    if proc is None or proc.poll() is not None:
        return
    kill_process_tree(proc.pid)


def stream_logs(pipe, prefix_color: str, prefix_text: str):
    """Stream stdout/stderr from subprocess with formatted prefix."""
    try:
        for line in iter(pipe.readline, ""):
            if not line:
                break
            clean_line = line.rstrip("\r\n")
            print(f"{prefix_color}{COLOR_BOLD}[{prefix_text}]{COLOR_RESET} {clean_line}")
    except (ValueError, OSError):
        pass
    finally:
        try:
            pipe.close()
        except Exception:
            pass


def run_in_separate_windows(python_exe: str, npm_exe: str, host: str, port: int, reload: bool):
    """Launch backend and frontend in separate Windows cmd terminals."""
    if sys.platform != "win32":
        print(f"{COLOR_YELLOW}[warning] --separate is currently designed for Windows.{COLOR_RESET}")
        return

    reload_flag = "--reload" if reload else ""
    backend_cmd = f'title InternIQ Backend (FastAPI) && cd /d "{ROOT_DIR}" && "{python_exe}" -m uvicorn backend.main:app {reload_flag} --host {host} --port {port}'
    frontend_cmd = f'title InternIQ Frontend (Vite) && cd /d "{FRONTEND_DIR}" && "{npm_exe}" run dev'

    print(f"{COLOR_GREEN}Launching Backend and Frontend in separate windows...{COLOR_RESET}")
    subprocess.Popen(f'start "InternIQ Backend" cmd /k "{backend_cmd}"', shell=True)
    subprocess.Popen(f'start "InternIQ Frontend" cmd /k "{frontend_cmd}"', shell=True)
    print(f"{COLOR_CYAN}Both services launched successfully.{COLOR_RESET}")


def run_unified(python_exe: str, npm_exe: str, host: str, port: int, reload: bool):
    """Launch both processes concurrently and merge their output streams."""
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["FORCE_COLOR"] = "1"

    backend_args = [
        python_exe,
        "-u",
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    if reload:
        backend_args.append("--reload")

    frontend_args = [npm_exe, "run", "dev"]

    print(f"{COLOR_DIM}Starting backend process: {' '.join(backend_args)}{COLOR_RESET}")
    backend_proc = subprocess.Popen(
        backend_args,
        cwd=str(ROOT_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        env=env,
    )

    print(f"{COLOR_DIM}Starting frontend process: {' '.join(frontend_args)}{COLOR_RESET}")
    frontend_proc = subprocess.Popen(
        frontend_args,
        cwd=str(FRONTEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        env=env,
    )

    # Start reader threads
    backend_thread = threading.Thread(
        target=stream_logs,
        args=(backend_proc.stdout, COLOR_CYAN, "backend"),
        daemon=True,
    )
    frontend_thread = threading.Thread(
        target=stream_logs,
        args=(frontend_proc.stdout, COLOR_GREEN, "frontend"),
        daemon=True,
    )

    backend_thread.start()
    frontend_thread.start()

    print(f"\n{COLOR_BOLD}{COLOR_GREEN}[*] Both servers are running! Press Ctrl+C at any time to stop.{COLOR_RESET}\n")

    shutdown_event = threading.Event()

    def signal_handler(signum, frame):
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, signal_handler)

    try:
        while not shutdown_event.is_set():
            # Check if either process exited unexpectedly
            b_poll = backend_proc.poll()
            f_poll = frontend_proc.poll()

            if b_poll is not None:
                print(f"\n{COLOR_RED}[runner] Backend process terminated with exit code {b_poll}.{COLOR_RESET}")
                break
            if f_poll is not None:
                print(f"\n{COLOR_RED}[runner] Frontend process terminated with exit code {f_poll}.{COLOR_RESET}")
                break

            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        print(f"\n{COLOR_YELLOW}[runner] Shutting down servers...{COLOR_RESET}")
        terminate_proc(backend_proc)
        terminate_proc(frontend_proc)
        print(f"{COLOR_GREEN}[runner] All processes terminated cleanly.{COLOR_RESET}")


def main():
    parser = argparse.ArgumentParser(
        description="InternIQ Full-Stack Dev Launcher (FastAPI Backend + Vite Frontend)"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Backend host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Backend port (default: 8000)")
    parser.add_argument(
        "--no-reload", action="store_true", help="Disable auto-reload for uvicorn"
    )
    parser.add_argument(
        "--separate",
        "-s",
        action="store_true",
        help="Launch backend and frontend in separate command prompt windows (Windows only)",
    )
    parser.add_argument(
        "--kill-existing",
        "-k",
        action="store_true",
        help="Kill existing processes listening on port 8000 or 5173 before starting",
    )

    args = parser.parse_args()

    # Pre-flight checks
    try:
        python_exe = get_python_executable()
    except Exception as e:
        print(f"{COLOR_RED}Error resolving Python executable: {e}{COLOR_RESET}")
        sys.exit(1)

    try:
        npm_exe = get_npm_executable()
    except Exception as e:
        print(f"{COLOR_RED}Error: {e}{COLOR_RESET}")
        sys.exit(1)

    if not FRONTEND_DIR.exists():
        print(f"{COLOR_RED}Error: Frontend directory not found at {FRONTEND_DIR}{COLOR_RESET}")
        sys.exit(1)

    print("=" * 64)
    print(f"{COLOR_BOLD}{COLOR_CYAN}                InternIQ Development Launcher{COLOR_RESET}")
    print("=" * 64)
    print(f"Backend Target : {COLOR_CYAN}http://{args.host}:{args.port}{COLOR_RESET} (FastAPI / Uvicorn)")
    print(f"Frontend Target: {COLOR_GREEN}http://localhost:5173{COLOR_RESET} (React / Vite)")
    print(f"Python Executable: {COLOR_DIM}{python_exe}{COLOR_RESET}")
    print(f"Node / npm Executable: {COLOR_DIM}{npm_exe}{COLOR_RESET}")
    print("=" * 64)

    # Check / handle active ports
    if args.kill_existing:
        for p in [args.port, 5173]:
            pid = get_pid_using_port(p)
            if pid:
                print(f"{COLOR_YELLOW}Killing existing process PID {pid} on port {p}...{COLOR_RESET}")
                kill_process_tree(pid)
                time.sleep(0.5)
    else:
        if is_port_in_use(args.port, args.host):
            pid = get_pid_using_port(args.port)
            pid_info = f" (PID: {pid})" if pid else ""
            print(
                f"{COLOR_YELLOW}[!] Notice: Port {args.port} is currently in use{pid_info}."
                f"\n    Use --kill-existing to free it, or ensure old instances are stopped.{COLOR_RESET}\n"
            )
        if is_port_in_use(5173):
            pid = get_pid_using_port(5173)
            pid_info = f" (PID: {pid})" if pid else ""
            print(
                f"{COLOR_YELLOW}[!] Notice: Port 5173 is currently in use{pid_info}."
                f"\n    Vite may automatically switch to another port (e.g. 5174).{COLOR_RESET}\n"
            )

    if args.separate:
        run_in_separate_windows(
            python_exe=python_exe,
            npm_exe=npm_exe,
            host=args.host,
            port=args.port,
            reload=not args.no_reload,
        )
    else:
        run_unified(
            python_exe=python_exe,
            npm_exe=npm_exe,
            host=args.host,
            port=args.port,
            reload=not args.no_reload,
        )


if __name__ == "__main__":
    main()
