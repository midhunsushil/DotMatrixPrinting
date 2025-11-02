import jinja2
import win32print
from datetime import datetime

ESC = chr(27)
template_path = "template.j2"

def render_template(items):
    # context = {
    #     "ESC": ESC,
    #     "header": "DELIVERY NOTE",
    #     "footer": "Thank you for your business",
    #     "date": datetime.now().strftime("%d-%m-%Y"),
    #     "invoice_no": "001234",
    #     "customer": "Customer Name",
    #     "items": items,
    #     "grand_total": "{:.2f}".format(sum(float(r["total"]) for r in items))
    # }
    loader = jinja2.FunctionLoader(lambda name: open(template_path, encoding="utf-8").read())
    env = jinja2.Environment(loader=loader)  # trim_blocks=True, lstrip_blocks=True
    env.globals['chr'] = chr
    template = env.get_template(template_path)
    return template.render(items)

def print_raw_text(printer_name, text):
    hPrinter = win32print.OpenPrinter(printer_name)
    try:
        output = text   # Form feed
        raw_data = output.encode('cp437', errors='replace')
        job = win32print.StartDocPrinter(hPrinter, 1, ("Delivery Note", None, "RAW"))
        try:
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, raw_data)
            win32print.EndPagePrinter(hPrinter)
        finally:
            win32print.EndDocPrinter(hPrinter)
    finally:
        win32print.ClosePrinter(hPrinter)

# Manual test data
data = {
    'dn_number': 'DN-2025-001',
    'shipping_date': '2025-10-28',
    'items': [
        {'product': 'Fresh Apples', 'ordered': '50 kg', 'delivered': '50 kg'},
        {'product': 'Orange Juice', 'ordered': '24 pcs', 'delivered': '24 pcs'},
        {'product': 'Bread Loaves', 'ordered': '100 pcs', 'delivered': '98 pcs'}
    ]
}



if __name__ == '__main__':
    printer_name = "EPSON LQ-680 ESC/P2"  # Use your actual printer name
    output = render_template(data)
    print(output)
    print_raw_text(printer_name, output)