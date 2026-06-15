import os
from fpdf import FPDF


def generate_pdf(user_id, items, total_price):
    pdf = FPDF()
    pdf.add_page()

    font_path = os.path.join(os.getcwd(), 'fonts', "DejaVuSans-Bold.ttf")
    pdf.add_font("DejaVu", style="", fname=font_path)

    pdf.set_font("DejaVu", size=20)
    pdf.cell(190, 10, txt="PizzaFox", ln=True, align="C")

    pdf.ln(5)
    pdf.cell(190, 0, txt="=" * 66, ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("DejaVu", size=11)
    pdf.cell(190, 6, txt=f"Номер покупателя: #{user_id}", ln=True)
    pdf.ln(5)

    pdf.set_font("DejaVu", size=10)
    pdf.cell(100, 8, txt="Наименование")
    pdf.cell(30, 8, txt="Кол-во", align="C")
    pdf.cell(60, 8, txt="Всего", align="R")
    pdf.ln(10)

    pdf.set_font("DejaVu", size=11)
    for item in items:
        item_total = float(item['price']) * int(item['quantity'])
        pdf.cell(100, 8, txt=str(item['title']))
        pdf.cell(30, 8, txt=f"{item['quantity']} шт.", align="C")
        pdf.cell(60, 8, txt=f"{item_total:.2f} BYN", align="R")
        pdf.ln(8)

    pdf.ln(5)
    pdf.cell(190, 0, txt="-" * 160, ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("DejaVu", size=14)
    pdf.cell(130, 10, txt="ИТОГО К ОПЛАТЕ:", align="L")
    pdf.cell(60, 10, txt=f"{total_price:.2f} BYN", align="R")

    filename = f"receipt_{user_id}.pdf"
    pdf.output(filename)
    return filename