from lexi_core.llm import ask_lexi
from lexi_core.search import search_files
from lexi_core.memory import save_memory, load_recent_memory

def main():
    print("Lexi.PHYS Terminal Core")
    print("Type /quit to exit. Type /remember your note to save a memory.")
    while True:
        msg = input("\nyou> ").strip()
        if not msg:
            continue
        if msg.lower() in {"/quit", "quit", "exit"}:
            break
        if msg.startswith("/remember "):
            note = msg.replace("/remember ", "", 1).strip()
            save_memory("user_note", note, tags=["manual"])
            print("lexi> Memory locked.")
            continue

        save_memory("user", msg)
        chunks = search_files(msg, limit=5)
        memory = load_recent_memory(limit=20)
        try:
            reply = ask_lexi(msg, context_chunks=chunks, recent_memory=memory)
        except Exception as e:
            reply = f"Runtime error: {e}"
        save_memory("assistant", reply)
        print(f"\nlexi> {reply}")

if __name__ == "__main__":
    main()
