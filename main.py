import customtkinter as ctk
from tkinter import messagebox
from web3 import Web3
from private_key import PRIVATE_KEY

# Web3 Connection
arbitrum_url = 'https://arbitrum-mainnet.infura.io/v3/YOUR_INFURA_KEY'
w3 = Web3(Web3.HTTPProvider(arbitrum_url))

def check_connection():
    return w3.is_connected()

def mint_nft(seller_address, buyer_address, item_name, item_description, item_attributes):
    if not check_connection():
        messagebox.showerror("Error", "Blockchain connection failed.")
        return

    contract_address = 'YOUR_CONTRACT_ADDRESS'
    abi = [
        {
            "inputs": [
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "string", "name": "name", "type": "string"},
                {"internalType": "string", "name": "description", "type": "string"},
                {"internalType": "string", "name": "attributes", "type": "string"},
            ],
            "name": "mintNFT",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function",
        }
    ]

    try:
        contract = w3.eth.contract(address=contract_address, abi=abi)
        nonce = w3.eth.get_transaction_count(seller_address)

        txn = contract.functions.mintNFT(
            buyer_address,
            item_name,
            item_description,
            item_attributes
        ).build_transaction({
            'chainId': 42161,
            'gas': 2000000,
            'gasPrice': w3.to_wei('1', 'gwei'),
            'nonce': nonce,
        })

        signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
        txn_hash = w3.eth.send_raw_transaction(signed_txn['raw_transaction'])

        messagebox.showinfo("Success", f"NFT Minted!\nTransaction Hash:\n{txn_hash.hex()}")

    except Exception as e:
        error_message = str(e)

        # Handle insufficient funds specifically
        if "insufficient funds" in error_message.lower():
            messagebox.showwarning(
                "Insufficient Funds",
                "Transaction failed due to insufficient funds for gas.\n\n"
                "Please ensure the seller wallet has enough ETH on Arbitrum to cover gas fees."
            )
        else:
            messagebox.showerror("Minting Error", error_message)


class NFTApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NFT Game Item Marketplace")
        self.geometry("700x650")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.wm_iconbitmap("logo.ico")


        self.grid_columnconfigure(0, weight=1)

        # Wallet Frame
        self.wallet_frame = ctk.CTkFrame(self)
        self.wallet_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        ctk.CTkLabel(self.wallet_frame, text="Seller Address:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.seller_entry = ctk.CTkEntry(self.wallet_frame, width=500)
        self.seller_entry.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.wallet_frame, text="Buyer Address:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.buyer_entry = ctk.CTkEntry(self.wallet_frame, width=500)
        self.buyer_entry.grid(row=1, column=1, padx=10, pady=10)

        # Item Info
        self.item_frame = ctk.CTkFrame(self)
        self.item_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        ctk.CTkLabel(self.item_frame, text="Item Name:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.item_name_entry = ctk.CTkEntry(self.item_frame, width=500)
        self.item_name_entry.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.item_frame, text="Item Attributes:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.item_attr_entry = ctk.CTkEntry(self.item_frame, width=500)
        self.item_attr_entry.grid(row=1, column=1, padx=10, pady=10)

        # Description Frame
        self.desc_frame = ctk.CTkFrame(self)
        self.desc_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        ctk.CTkLabel(self.desc_frame, text="Item Description:").pack(anchor="w", padx=10, pady=(10, 5))
        self.description_box = ctk.CTkTextbox(self.desc_frame, height=100)
        self.description_box.pack(fill="both", padx=10, pady=(0, 10))

        self.generate_button = ctk.CTkButton(self.desc_frame, text="Generate Description", command=self.generate_description)
        self.generate_button.pack(pady=5)

        # Mint Button
        self.mint_button = ctk.CTkButton(self, text="Mint NFT", command=self.mint_nft_gui)
        self.mint_button.grid(row=3, column=0, pady=20)

    def generate_description(self):
        name = self.item_name_entry.get()
        attrs = self.item_attr_entry.get()

        if not name or not attrs:
            messagebox.showwarning("Warning", "Please enter item name and attributes first.")
            return

        description = f"{name} is a powerful NFT with the following attributes: {attrs}."
        self.description_box.delete("1.0", "end")
        self.description_box.insert("1.0", description)

    def mint_nft_gui(self):
        seller = self.seller_entry.get()
        buyer = self.buyer_entry.get()
        name = self.item_name_entry.get()
        attrs = self.item_attr_entry.get()

        if not all([seller, buyer, name, attrs]):
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        # Auto-generate description if user hasn’t customized it
        current_desc = self.description_box.get("1.0", "end").strip()
        if not current_desc or current_desc == "Enter item description here...":
            current_desc = f"{name} is a unique NFT with these traits: {attrs}."

        mint_nft(seller, buyer, name, current_desc, attrs)


if __name__ == "__main__":
    app = NFTApp()
    app.mainloop()
