"""Terminal interface."""

verbose = False

DIM    = "\033[2m"
BOLD   = "\033[1m"
CYAN   = "\033[36m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
RESET  = "\033[0m"

def banner(backend):
    print(f"\n{DIM}──────────────────────────────────{RESET}")
    print(f"{BOLD}  miniature{RESET}  {DIM}({backend}){RESET}")
    print(f"{DIM}──────────────────────────────────{RESET}\n")

def prompt():
    try:
        user = input(f"{BOLD}>{RESET} ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        return None
    return user if user and user not in ("quit", "exit", "q") else None

def agent_response(text):
    print(f"\n{CYAN}{text}{RESET}\n")

def tool_call(name, args):
    args_str = ", ".join(f"{k}={v!r}" for k, v in args.items())
    print(f"  {YELLOW}▸ {name}{RESET}{DIM}({args_str}){RESET}")

def tool_result(name, result):
    lines = str(result).strip().split("\n")
    preview = lines[0][:80] + ("…" if len(lines[0]) > 80 or len(lines) > 1 else "")
    print(f"    {GREEN}→{RESET} {DIM}{preview}{RESET}")

def verbose_prompt(messages, max_size=1024):
    if not verbose:
        return
    print(f"{DIM}── verbose prompt ──{RESET}")
    for m in messages:
        text = m["content"][:max_size] + ("…" if len(m["content"]) > max_size else "")
        print(f"{DIM}  [{m['role']}] {text}{RESET}")
    print(f"{DIM}────────────────{RESET}")

def goodbye():
    print(f"{DIM}bye{RESET}\n")
