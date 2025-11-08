import jinja2
import win32print
import pandas as pd
import escp2

ESC = chr(27)
template_path = "template.txt.jinja"

import arabic_reshaper
from bidi.algorithm import get_display


def convert_to_pc864(text):
    """Convert and prepare Arabic for PC864 printing"""
    # Reshape for proper character joining
    # reshaped = arabic_reshaper.reshape(text)
    # Get display order (RTL reversal)
    # display_text = get_display(reshaped)
    # Encode to PC864
    pc864_bytes = text.encode('cp720')
    # Decode back to string
    return pc864_bytes.decode('cp437')

def render_template(items):
    loader = jinja2.FileSystemLoader("templates")
    env = jinja2.Environment(loader=loader)  # trim_blocks=True, lstrip_blocks=True
    escp2.register_jinja_globals(env)
    template = env.get_template(template_path)
    data = {"products": create_table_escp2(getdata()[0]["products"])}
    # print(data)
    return template.render(data)

def print_raw_text(printer_name, text):
    hPrinter = win32print.OpenPrinter(printer_name)
    try:
        output = text   # Form feed
        raw_data = output.encode('cp437', errors="replace")
        # raw_data = text
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


def create_table_escp2(products):
    """Create ESC/P2 formatted table for dot matrix printer"""

    # ESC/P2 Commands
    SET_10CPI = b'\x1b\x4d'  # 12 CPI (Pica)
    SET_LEFT_MARGIN = b'\x1bl\x04\x00'  # Left margin = 4 chars (0x05 = 5 in decimal)
    SET_RIGHT_MARGIN = b'\x1bQ\x62\x00'  # Right margin at column 98
    LF = b'\n'  # Line feed
    CR = b'\r'  # Carriage return

    output = b''

    # Initialize printer
    output += SET_10CPI
    output += SET_LEFT_MARGIN + SET_RIGHT_MARGIN

    # Column widths
    PRODUCT_WIDTH = 47
    ORDERED_WIDTH = 7
    DELIVERED_WIDTH = 9
    UOM_WIDTH = 26

    def bold_text(text):
        SET_BOLD = ESC + 'E'  # Set Bold
        UNSET_BOLD = ESC + 'F'  # Unset bold
        return SET_BOLD + text + UNSET_BOLD

    # Helper function to wrap text
    def wrap_text(text, width):
        """Wrap text to fit column width"""
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= width:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        return lines if lines else [""]

    # Helper function to pad text
    def pad_text(text, width, align="left"):
        """Pad text to exact width"""
        text = str(text)[:width]
        if align == "left":
            return text.ljust(width)
        elif align == "right":
            return text.rjust(width)
        else:
            return text.center(width)

    # Table top border
    border_top = b"\xda" + b"\xc4" * PRODUCT_WIDTH + b"\xc2" + b"\xc4" * ORDERED_WIDTH + b"\xc2" + b"\xc4" * DELIVERED_WIDTH + b"\xc2" + b"\xc4" * UOM_WIDTH + b"\xbf"
    border_bottom = b"\xc0" + b"\xc4" * PRODUCT_WIDTH + b"\xc1" + b"\xc4" * ORDERED_WIDTH + b"\xc1" + b"\xc4" * DELIVERED_WIDTH + b"\xc1" + b"\xc4" * UOM_WIDTH + b"\xd9"
    border_between = b"\xc3" + b"\xc4" * PRODUCT_WIDTH + b"\xc5" + b"\xc4" * ORDERED_WIDTH + b"\xc5" + b"\xc4" * DELIVERED_WIDTH + b"\xc5" + b"\xc4" * UOM_WIDTH + b"\xb4"
    seperator_char = b'\xb3'.decode('cp437')
    output += border_top + CR + LF

    # Table header
    header = seperator_char + bold_text(pad_text("Product", PRODUCT_WIDTH)) + seperator_char + bold_text(pad_text("Ordered", ORDERED_WIDTH,
                                                                       "center")) + seperator_char + bold_text(pad_text("Delivered",
                                                                                                 DELIVERED_WIDTH,
                                                                                                 "center")) + seperator_char + bold_text(pad_text("Unit", UOM_WIDTH,
                                                                       "center")) + seperator_char
    output += header.encode('cp437') + CR + LF

    # Header bottom border
    output += border_between + CR + LF

    # Table rows for products
    for j, product in enumerate(products):
        product_name = product['product']
        ordered = product['qty']
        delivered = product['qty_done']
        uom = product['uom']

        # Wrap product name if too long
        product_lines = wrap_text(product_name, PRODUCT_WIDTH)
        uom_lines = wrap_text(uom, UOM_WIDTH)

        for i in range(max(len(product_lines), len(uom_lines))):
            product_line_val = product_lines[i] if i < len(product_lines) else ""
            uom_line_val = uom_lines[i] if i < len(uom_lines) else ""
            if i == 0:
                # First line with data
                row = seperator_char + pad_text(product_line_val, PRODUCT_WIDTH) + seperator_char + pad_text(ordered, ORDERED_WIDTH,
                                                                           "center") + seperator_char + pad_text(delivered,
                                                                                                     DELIVERED_WIDTH,
                                                                                                     "center") + seperator_char + pad_text(uom_line_val,
                                                                                                     UOM_WIDTH,
                                                                                                     "center") + seperator_char
            else:
                # Continuation lines (empty qty columns)
                row = seperator_char + pad_text(product_line_val, PRODUCT_WIDTH) + seperator_char + pad_text("", ORDERED_WIDTH) + seperator_char + pad_text("",
                                                                                                               DELIVERED_WIDTH) + seperator_char + pad_text(uom_line_val, UOM_WIDTH, "center") + seperator_char

            output += row.encode('cp437') + CR + LF

        border = border_bottom if j+1 == len(products) else border_between
        output += border + CR + LF

    return output.decode('cp437')


def getdata():
    # Read the Excel file
    df = pd.read_excel('Transfer (stock.picking) (35).xlsx')

    # Extract delivery notes with their products
    delivery_notes = []

    # Iterate through rows to find delivery notes (rows with Reference value)
    for idx, row in df.iterrows():
        if pd.notna(row['Reference']):
            # This is a delivery note row: Contains DN info + 1 product details
            dn_info = {
                "Reference": str(row['Reference']),
                "Date": pd.Timestamp(row['Scheduled Date']).strftime('%Y-%m-%d %H:%M:%S'),
                "Source Location": str(row['Source Location']) if pd.notna(row['Source Location']) else "",
                "Source Location/Barcode": str(row['Source Location/Barcode']) if 'Source Location/Barcode' in df.columns and pd.notna(
                    row['Source Location/Barcode']) else "",
                "Destination Location": str(row['Destination Location']) if pd.notna(
                    row['Destination Location']) else "",
                "Destination Location/Barcode": str(row['Destination Location/Barcode']) if pd.notna(
                    row['Destination Location/Barcode']) else "",
                "products": []
            }

            # Add first product from this row
            product = {
                "product": str(row['Operations/Product']) or "",
                "qty": str(row['Operations/Quantity']) or "",
                "qty_done": str(row['Operations/Qty Done']) or "",
                "uom": str(row['Operations/Unit of Measure']) or ""
            }
            dn_info["products"].append(product)
            delivery_notes.append(dn_info)

        elif pd.isna(row['Reference']) and pd.notna(row['Operations/Product']):
            # This is a product row. Add this product to the latest dn_info.
            product = {
                "product": str(row['Operations/Product']) or "",
                "qty": str(row['Operations/Quantity']) or "",
                "qty_done": str(row['Operations/Qty Done']) or "",
                "uom": str(row['Operations/Unit of Measure']) or ""
            }
            latest_dn_info = delivery_notes[-1]
            latest_dn_info["products"].append(product)

    # # Or save to file
    # with open('delivery_notes.json', 'w', encoding='utf-8') as f:
    #     json.dump(delivery_notes, f, indent=2, ensure_ascii=False)

    return delivery_notes


if __name__ == '__main__':
    printer_name = "EPSON LQ-680 ESC/P2"  # Use your actual printer name
    output = render_template(data)
    print(output)
    # getdata()
    # Usage
    # arabic_text = "[GS019] Al-Dair Primary & Intermediate School for Girls | مدرسة الدير الابتدائية الإعدادية للبنات"
    # pc864_text = convert_to_pc864(arabic_text)
    # print(pc864_text)
    # print_raw_text(printer_name, output)