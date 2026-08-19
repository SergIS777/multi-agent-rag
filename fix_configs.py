import pathlib

BLOCK = "\n\ncost:\n  max_tokens_per_query: 4000\n"

for n in ["law", "logistics", "medicine", "realestate"]:
    p = pathlib.Path("configs") / f"{n}.yaml"
    t = p.read_text(encoding="utf-8")
    if "cost:" in t:
        print(f"{n}: cost уже есть — не трогаю")
    else:
        p.write_text(t.rstrip() + BLOCK, encoding="utf-8")
        print(f"{n}: cost добавлен")