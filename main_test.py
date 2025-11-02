from jinja2 import Environment, FileSystemLoader
import csv, sys
import escp2

def load_template(dir_path="templates", name="delivery_note.txt.j2"):
    env = Environment(loader=FileSystemLoader(dir_path), trim_blocks=True, lstrip_blocks=True)
    # allow calling functions from the template
    env.globals.update(esc={
        "init": escp2.init(),
        "bold_on": escp2.bold_on(),
        "bold_off": escp2.bold_off(),
        "page_setup": escp2.page_setup,
        "formfeed": escp2.form_feed(),
    })
    return env.get_template(name)

def row_to_context(row):
    items = []  # build from your CSV schema; here’s a sketch
    # For “one delivery note per row” you may need to parse a JSON column or fetch items by DN id
    items = [
        {"name": row["item1_name"], "qty": int(row["item1_qty"]), "rate": float(row["item1_rate"]), "amount": float(row["item1_amount"])},
        # ...
    ]
    return {
        "doc": {"number": row["dn_number"], "date": row["dn_date"], "customer_name": row["customer_name"]},
        "items": items,
        "totals": {"grand": sum(i["amount"] for i in items)},
    }

def print_raw(raw_bytes, printer_name=None):
    # Windows
    try:
        import win32print, win32api
        hPrinter = win32print.OpenPrinter(printer_name or win32print.GetDefaultPrinter())
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("DN", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)
        win32print.WritePrinter(hPrinter, raw_bytes)
        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
        win32print.ClosePrinter(hPrinter)
        return
    except Exception:
        pass
    # Linux / macOS (CUPS)
    import subprocess, tempfile, os
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(raw_bytes)
        tmp = f.name
    try:
        subprocess.run(["lp", "-o", "raw", tmp], check=True)
    finally:
        os.unlink(tmp)

def main(csv_path):
    tmpl = load_template()
    with open(csv_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ctx = row_to_context(row)
            text = tmpl.render(**ctx)
            print_raw(text.encode("latin1", errors="replace"))

if __name__ == "__main__":
    main(sys.argv[1])
