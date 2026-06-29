import sys
try:
    import PyPDF2
except ImportError:
    print("PyPDF2 not installed")
    sys.exit(0)

reader = PyPDF2.PdfReader("Sprint 0_ cargoservice_Annot.pdf")
for i, page in enumerate(reader.pages):
    if "/Annots" in page:
        for annot in page["/Annots"]:
            obj = annot.get_object()
            print(f"Page {i+1}: {obj.get('/Subtype')} - {obj.get('/Contents')}")
