import qrcode

def create_qr(url: str, filename: str = "url_qr.png"):
    qr = qrcode.make(url)
    qr.save(filename)
    print(f" QR code save as {filename}")

if __name__ == "__main__":
    url = input("Enter a URL to generate QR code: ").strip()
    if url:
        create_qr(url)
    else:
        print("Please provide a URL")

