import pandas as pd
import xml.etree.ElementTree as ET
from tkinter import Tk, filedialog, ttk
import tkinter as tk

def parse_xml(file_path):
    # Parsear el archivo XML
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Espacio de nombres en el XML
    namespace = {'ns': 'urn:iso:std:iso:20022:tech:xsd:pain.008.001.02'}

    # Extraer información de transacciones
    transactions = []
    for tx in root.findall('.//ns:DrctDbtTxInf', namespace):
        transaction = {
            "EndToEndId": tx.find('.//ns:EndToEndId', namespace).text,
            "Amount": float(tx.find('.//ns:InstdAmt', namespace).text),
            "Currency": tx.find('.//ns:InstdAmt', namespace).attrib['Ccy'],
            "DebtorName": tx.find('.//ns:Dbtr/ns:Nm', namespace).text,
            "DebtorIBAN": tx.find('.//ns:DbtrAcct/ns:Id/ns:IBAN', namespace).text,
            "MandateId": tx.find('.//ns:MndtId', namespace).text,
            "SignatureDate": tx.find('.//ns:DtOfSgntr', namespace).text,
        }
        transactions.append(transaction)

    # Extraer información del grupo principal
    group_data = {
        "MessageId": root.find('.//ns:MsgId', namespace).text,
        "CreationDateTime": root.find('.//ns:CreDtTm', namespace).text,
        "NumberOfTransactions": root.find('.//ns:NbOfTxs', namespace).text,
        "ControlSum": root.find('.//ns:CtrlSum', namespace).text,
        "InitiatingPartyName": root.find('.//ns:InitgPty/ns:Nm', namespace).text,
    }

    return transactions, group_data

def display_transactions(transactions, group_data):
    # Crear la ventana principal
    root = tk.Tk()
    root.title("Contenido del archivo XML")

    # Mostrar datos generales en etiquetas
    tk.Label(root, text=f"Message ID: {group_data['MessageId']}").pack(anchor="w")
    tk.Label(root, text=f"Creation DateTime: {group_data['CreationDateTime']}").pack(anchor="w")
    tk.Label(root, text=f"Number of Transactions: {group_data['NumberOfTransactions']}").pack(anchor="w")
    tk.Label(root, text=f"Control Sum: {group_data['ControlSum']}").pack(anchor="w")
    tk.Label(root, text=f"Initiating Party Name: {group_data['InitiatingPartyName']}").pack(anchor="w")

    # Crear un Treeview para mostrar los datos de transacciones
    tree = ttk.Treeview(root, columns=("EndToEndId", "Amount", "Currency", "DebtorName", "DebtorIBAN", "MandateId", "SignatureDate"), show='headings')

    # Definir encabezados
    tree.heading("EndToEndId", text="EndToEndId")
    tree.heading("Amount", text="Amount")
    tree.heading("Currency", text="Currency")
    tree.heading("DebtorName", text="DebtorName")
    tree.heading("DebtorIBAN", text="DebtorIBAN")
    tree.heading("MandateId", text="MandateId")
    tree.heading("SignatureDate", text="SignatureDate")

    # Ajustar el ancho de las columnas
    for col in ("EndToEndId", "Amount", "Currency", "DebtorName", "DebtorIBAN", "MandateId", "SignatureDate"):
        tree.column(col, width=150, anchor="center")

    # Insertar datos en el Treeview
    for transaction in transactions:
        tree.insert("", tk.END, values=(transaction["EndToEndId"], transaction["Amount"], transaction["Currency"], transaction["DebtorName"], transaction["DebtorIBAN"], transaction["MandateId"], transaction["SignatureDate"]))

    # Empaquetar el Treeview
    tree.pack(fill=tk.BOTH, expand=True)

    # Ejecutar el bucle principal de la ventana
    root.mainloop()

def main():
    # Crear una ventana para seleccionar el archivo
    root = Tk()
    root.withdraw()  # Ocultar la ventana principal
    file_path = filedialog.askopenfilename(title="Seleccionar archivo XML", filetypes=[("Archivos XML", "*.xml")])

    if file_path:
        transactions, group_data = parse_xml(file_path)
        display_transactions(transactions, group_data)
    else:
        print("No se seleccionó ningún archivo.")

if __name__ == "__main__":
    main()
