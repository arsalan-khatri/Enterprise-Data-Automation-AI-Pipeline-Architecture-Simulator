import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

NUM_RECORDS = 10_000
OUTPUT_DIR = Path("data/raw")
OUTPUT_FILE = OUTPUT_DIR / "customer_tickets.csv"

random.seed(42)

# ============================================================
# DATA OPTIONS
# ============================================================

CUSTOMER_TYPES = [
    "Regular",
    "Premium",
    "Business"
]

DEPARTMENTS = [
    "Logistics",
    "Payments",
    "Returns",
    "Technical Support",
    "Sales",
    "Account Support"
]

STATUSES = [
    "Open",
    "In Progress",
    "Resolved"
]

# ============================================================
# CUSTOMER MESSAGE TEMPLATES
# ============================================================

MESSAGE_TEMPLATES = {

    # "Logistics": [
    #     "My order has not arrived yet.",
    #     "My package is delayed and I need an update.",
    #     "I was supposed to receive my order yesterday but it has not arrived.",
    #     "Can you tell me where my order is?",
    #     "My delivery is taking much longer than expected.",
    #     "The tracking information has not been updated.",
    #     "My package was supposed to arrive five days ago.",
    #     "I received a notification that my order was delivered, but I did not receive it.",
    #     "I need help tracking my order.",
    #     "Why is my order still stuck in transit?"
    # ],

    "Logistics": [
        "My order has not arrived yet.",
        "My package is delayed and I need an update.",
        "I was supposed to receive my order yesterday but it has not arrived.",
        "Can you tell me where my order is?",
        "My delivery is taking much longer than expected.",
        "The tracking information has not been updated.",
        "My package was supposed to arrive five days ago.",
        "I received a notification that my order was delivered, but I did not receive it.",
        "I need help tracking my order.",
        "Why is my order still stuck in transit?",
        "The tracking link you sent me is broken.",
        "Can I change the shipping address for my order? I made a mistake.",
        "My package was left out in the rain and the box is completely ruined.",
        "The delivery guy didn't even ring the bell, he just left it at the gate.",
        "I need this order by Friday, will it reach on time?",
        "Tracking says 'Out for Delivery' for the past two days.",
        "I missed the delivery attempt yesterday, how can I reschedule it?",
        "The courier is asking for extra cash for delivery, is this normal?",
        "My tracking shows it was delivered to a neighbor, but they don't have it.",
        "I ordered two items, but only one came in the box.",
        "Can you ask the driver to call me before arriving?",
        "I want to cancel this order, the shipping is taking way too long.",
        "My package seems to be bouncing between two different sorting facilities.",
        "How do I report a missing package?",
        "Is there a way to expedite my shipping? I am willing to pay extra.",
        "The estimated delivery date keeps changing every single day.",
        "Tracking status says 'Exception', what does that mean?",
        "I put the wrong zip code on my shipping address, can we fix it before dispatch?",
        "Do your courier partners deliver on weekends?",
        "The delivery attempted notification is wrong, I was home all day!",
        "My package was delivered to the wrong house down the street.",
        "I received someone else's order by mistake.",
        "It's been three weeks and my international shipment hasn't cleared customs.",
        "The driver refused to bring the heavy box up to my apartment.",
        "Why haven't I received a dispatch email yet? It's been 3 days since I ordered.",
        "The package was torn open when I received it.",
        "Your delivery partner keeps calling the wrong phone number.",
        "Can I just pick up the order from the warehouse directly?",
        "Tracking says 'Returned to Sender', why did that happen?",
        "I need to hold my shipment because I am going out of town tomorrow.",
        "The shipping box was fine, but the product box inside is completely crushed.",
        "Is it possible to schedule a specific delivery window for tomorrow?",
        "My tracking number is invalid or not recognized by the carrier website.",
        "I paid for overnight shipping, but it's been 48 hours. I want my shipping fee refunded.",
        "I keep getting automated replies, I need a real person to check my shipment status.",
        "The package is too big to fit in my locker, where will they leave it?",
        "Can you leave instructions for the driver to leave the package at the back door?",
        "Why is my shipment stuck at the local hub for the last 4 days?",
        "I haven't gotten any updates since the shipping label was created last week.",
        "The courier marked it as undeliverable, but my address is perfectly clear."
    ],

    # "Payments": [
    #     "My payment failed but the amount was deducted.",
    #     "I was charged twice for the same order.",
    #     "The payment page is not working.",
    #     "I cannot complete my payment.",
    #     "My card was charged but the order was not confirmed.",
    #     "The transaction failed several times.",
    #     "I was charged an incorrect amount.",
    #     "I need help with a payment issue.",
    #     "The payment was deducted but I did not receive an order confirmation.",
    #     "Why was my payment declined?"
    # ],

    "Payments": [
        "My payment failed but the amount was deducted.",
        "I was charged twice for the same order.",
        "The payment page is not working.",
        "I cannot complete my payment.",
        "My card was charged but the order was not confirmed.",
        "The transaction failed several times.",
        "I was charged an incorrect amount.",
        "I need help with a payment issue.",
        "The payment was deducted but I did not receive an order confirmation.",
        "Why was my payment declined?",
        "I applied a promo code but was still charged the full price.",
        "Do you accept PayPal or Apple Pay?",
        "My bank says the transaction went through, but your system says it failed.",
        "I need a tax invoice for my recent purchase.",
        "The website timed out while processing my payment, what should I do?",
        "Can I split my payment across two different credit cards?",
        "I'm seeing a strange pending charge on my bank statement from your company.",
        "I tried to use my gift card, but it says the balance is zero.",
        "Is there an option to pay in installments?",
        "I selected Cash on Delivery but was asked to pay online.",
        "The billing address on my receipt is wrong, can you update it?",
        "My credit card keeps getting rejected for no reason.",
        "Are there any hidden fees? My total looks higher than expected.",
        "How do I remove a saved credit card from my account?",
        "I was charged for shipping even though my order qualified for free delivery.",
        "The OTP for my card verification never arrived.",
        "I made a typo in my billing details, will my payment still go through?",
        "I keep getting an 'Error 500' when trying to check out.",
        "I accidentally placed the order twice because the payment button lagged.",
        "You charged my card yesterday, but the order is still showing as 'Pending Payment'.",
        "Can I pay using a different currency?",
        "Why is there an extra foreign transaction fee on my statement?",
        "My installment plan failed this month, how can I manually pay it?",
        "I received a notification of a payment, but I didn't buy anything!",
        "How long does it take for a failed transaction to bounce back to my account?",
        "The 3D secure authentication page is just a blank white screen.",
        "Can I get a receipt emailed to my work address instead?",
        "I tried paying with my debit card but it says 'Credit Cards Only'.",
        "My subscription renewed automatically but I wanted to cancel it.",
        "I want to change the payment method for my pre-order before it ships.",
        "The payment gateway is looping endlessly after I hit submit.",
        "Why is my Apple Pay failing at checkout?",
        "I paid via bank transfer, where do I upload the payment slip?",
        "You deducted money from my wallet but the checkout still asks for payment.",
        "I thought the first month was free, why was I charged immediately?",
        "I used a prepaid Visa card and the system won't accept it.",
        "My payment is stuck in 'Processing' status for the last 3 hours.",
        "Can I add a VAT number to my payment invoice?",
        "My discount code expired while I was stuck on the broken payment page.",
        "Is it safe to save my card details on your platform?"
    ],

    # "Returns": [
    #     "I want to return the product I received.",
    #     "The product arrived damaged and I want a replacement.",
    #     "I received the wrong product.",
    #     "How can I request a refund?",
    #     "I want to cancel my order and get my money back.",
    #     "The product does not match the description.",
    #     "I received a defective item.",
    #     "Please help me with the return process.",
    #     "I am not satisfied with the product and want to return it.",
    #     "When will I receive my refund?"
    # ],

    "Returns": [
        "I want to return the product I received.",
        "The product arrived damaged and I want a replacement.",
        "I received the wrong product.",
        "How can I request a refund?",
        "I want to cancel my order and get my money back.",
        "The product does not match the description.",
        "I received a defective item.",
        "Please help me with the return process.",
        "I am not satisfied with the product and want to return it.",
        "When will I receive my refund?",
        "The shirt I ordered is way too small, how do I exchange it?",
        "I received a blue case but I ordered a black one.",
        "The item broke the first time I used it, I need a refund.",
        "Where can I drop off my return package?",
        "Do I have to pay for return shipping?",
        "Can you send me a return shipping label?",
        "I returned my item a week ago but haven't gotten my money back.",
        "The box was fine, but the glass inside was completely shattered.",
        "I want to return this, it feels very cheap and low quality.",
        "I got an email saying my refund was processed, but it's not in my bank.",
        "Can I return an item I bought on clearance sale?",
        "I lost the original packaging, can I still return the item?",
        "My order is missing the charging cable, can you just send that part?",
        "I ordered this by mistake, please cancel it before it ships.",
        "I was sent two left shoes! I need a replacement immediately.",
        "The return courier was supposed to pick up the package yesterday but didn't come.",
        "I want to exchange this for a different color.",
        "Your return portal keeps giving me an error when I try to submit.",
        "I received this as a gift, can I return it for store credit?",
        "The product is totally different from the pictures on your website.",
        "How many days do I have to return this item?",
        "I only received a partial refund, why wasn't the full amount refunded?",
        "Can I return my online order at one of your physical stores?",
        "The instruction manual is missing, so I can't use it. I want to return it.",
        "I canceled my order 10 minutes after placing it, why is it still shipping?",
        "The expiration date on this product has already passed! I want my money back.",
        "I want to return 2 items out of the 5 I ordered in that package.",
        "My return tracking says 'Delivered to Warehouse' but my refund is still pending.",
        "You charged a restocking fee, but the website said free returns!",
        "This appliance won't turn on out of the box, I need an immediate replacement.",
        "The clothes smell like chemicals, I'm returning the whole order.",
        "I missed the 30-day return window by one day, can you make an exception?",
        "I initiated a return but changed my mind, how do I cancel the return request?",
        "Will my shipping fee be refunded if I return the item?",
        "I need a replacement, but I want to make sure it's packed properly this time.",
        "The dimensions listed online are wrong, it doesn't fit my space. Returning it.",
        "How do I print the return label if I don't have a printer?",
        "You sent me someone else's order! I want a refund and a return label.",
        "My refund went to a canceled credit card, what do I do?",
        "I am extremely disappointed with this purchase and demand a full refund."
    ],

    # "Technical Support": [
    #     "The application is not working properly.",
    #     "I cannot log into my account.",
    #     "The website keeps showing an error.",
    #     "The application crashes whenever I try to open it.",
    #     "I am unable to reset my password.",
    #     "The system is very slow today.",
    #     "I keep getting an error when trying to place an order.",
    #     "The website is not loading correctly.",
    #     "My account login is not working.",
    #     "I need technical help with the application."
    # ],

    "Technical Support": [
        "The application is not working properly.",
        "I cannot log into my account.",
        "The website keeps showing an error.",
        "The application crashes whenever I try to open it.",
        "I am unable to reset my password.",
        "The system is very slow today.",
        "I keep getting an error when trying to place an order.",
        "The website is not loading correctly.",
        "My account login is not working.",
        "I need technical help with the application.",
        "I requested a password reset email but never received it.",
        "The app freezes every time I try to add an item to the cart.",
        "I keep getting an 'Error 404' when clicking on my profile.",
        "My Two-Factor Authentication (2FA) code is not being accepted.",
        "The website layout looks completely broken on my mobile phone.",
        "I am stuck in an endless login loop; it keeps asking for my credentials.",
        "Why is the search bar not returning any results today?",
        "I updated the app on iOS and now it won't even open.",
        "Every time I click 'Checkout', the page just refreshes.",
        "Are your servers down? I can't access the platform at all.",
        "I keep getting a 'Session Expired' message the moment I log in.",
        "The images on the product pages are not loading for me.",
        "My account says it's locked due to too many failed login attempts.",
        "I can't upload my profile picture, it keeps saying 'File type not supported'.",
        "The chat widget on your website is covering the 'Buy' button.",
        "I am getting an 'Error 500: Internal Server Error' on the payment page.",
        "The app drains my battery really fast after the last update.",
        "How do I clear the cache? Support told me to do it but I don't know how.",
        "The website works fine on Chrome, but it is completely broken on Safari.",
        "I try to download my invoice PDF and nothing happens.",
        "My screen goes completely white when I navigate to the settings page.",
        "The links in your promotional email are leading to a dead page.",
        "I keep getting logged out randomly while browsing.",
        "The 'Save Changes' button in my account settings is grayed out and unclickable.",
        "Is there a bug with the wish list? All my saved items disappeared.",
        "The biometric login (Face ID) stopped working on my phone.",
        "I am getting push notifications, but when I click them, the app shows an error.",
        "Can you help me? The captcha verification is failing every single time.",
        "The dark mode toggle isn't working on the desktop version.",
        "I keep seeing the loading spinner forever when I try to apply a filter.",
        "Your website is flagged as 'Not Secure' by my antivirus software.",
        "The date picker for scheduling delivery is completely frozen.",
        "I can't type anything into the contact form, the keyboard won't pop up.",
        "I am trying to sync my account across devices but it's not updating.",
        "The voice search feature in the app doesn't recognize anything I say.",
        "My browser console is showing a bunch of JavaScript errors on your site.",
        "I deleted the app and reinstalled it, but the same bug is still happening.",
        "The video review won't play, it just buffers infinitely.",
        "It says my email address is invalid, but I've been using it for years.",
        "Can someone from IT look into my account? The data is completely corrupted."
    ],

    # "Sales": [
    #     "I want to know more about this product.",
    #     "Do you have this product available?",
    #     "Can I get a discount on a large order?",
    #     "I would like to know the current price.",
    #     "Are there any offers available?",
    #     "Can someone help me choose the right product?",
    #     "I want to place a business order.",
    #     "Do you offer bulk purchasing?",
    #     "I need more information before placing my order.",
    #     "Can you tell me about your available products?"
    # ],

    "Sales": [
        "I want to know more about this product.",
        "Do you have this product available?",
        "Can I get a discount on a large order?",
        "I would like to know the current price.",
        "Are there any offers available?",
        "Can someone help me choose the right product?",
        "I want to place a business order.",
        "Do you offer bulk purchasing?",
        "I need more information before placing my order.",
        "Can you tell me about your available products?",
        "When will the 'Out of Stock' item be available again?",
        "Do you offer student discounts or military discounts?",
        "Is there a size guide available for this clothing line?",
        "Can you tell me the exact dimensions of this furniture piece?",
        "I am looking for a laptop for video editing, what do you recommend?",
        "Will this phone case fit the newest model that just came out?",
        "Can I pre-order the new console before it officially launches?",
        "Do you guys price-match if I found this cheaper on another website?",
        "What is the warranty period for this appliance?",
        "I need to order 50 units for my company, who should I talk to?",
        "Can you send me a product catalog with wholesale pricing?",
        "Is this material 100% cotton or a synthetic blend?",
        "Do you offer free installation if I buy this air conditioner?",
        "I am setting up a new office, can I get a dedicated sales rep to help me?",
        "Are these shoes suitable for wide feet?",
        "What's the difference between the 'Pro' and the 'Standard' version?",
        "Is there an upcoming Black Friday sale I should wait for?",
        "Can I get a sample of this fabric before I place a large order?",
        "I'm a tax-exempt organization, how do I apply that to my purchase?",
        "Does this smart home device work with Google Assistant?",
        "If I buy the camera, does it come with a memory card included?",
        "Can I customize the color of this product?",
        "Do you have this exact model available at your physical store in downtown?",
        "How much would shipping cost if I buy three of these?",
        "Are there any hidden subscription fees with this software purchase?",
        "I saw a promo code on Instagram but it's not working, can you help?",
        "Does this product come in a gift box?",
        "I need advice on which skincare routine is best for dry skin.",
        "Can I set up a recurring monthly order for these coffee beans?",
        "Are the spare parts for this drone easy to find if it breaks?",
        "Is this item eligible for your 30-day money-back guarantee?",
        "I am trying to compare this model with your competitor's, why is yours better?",
        "Can I pay using a purchase order (PO)?",
        "Do you offer any loyalty programs for frequent buyers?",
        "If I buy the bundled package, how much am I actually saving?",
        "What voltage does this electronic device support? I'm taking it overseas.",
        "Is the carrying case included or do I have to buy it separately?",
        "Can you notify me via email as soon as this gets restocked?",
        "I want to buy gift cards for my team, is there a corporate rate?",
        "I have a few technical questions about the specs before I hit the buy button."
    ],

    # "Account Support": [
    #     "I cannot access my account.",
    #     "I need to update my account information.",
    #     "How can I change my email address?",
    #     "I forgot my account password.",
    #     "My account information is incorrect.",
    #     "I want to update my phone number.",
    #     "My account has been locked.",
    #     "I need help changing my personal information.",
    #     "I am having trouble verifying my account.",
    #     "How can I update my profile?"
    # ]

    "Account Support": [
        "I cannot access my account.",
        "I need to update my account information.",
        "How can I change my email address?",
        "I forgot my account password.",
        "My account information is incorrect.",
        "I want to update my phone number.",
        "My account has been locked.",
        "I need help changing my personal information.",
        "I am having trouble verifying my account.",
        "How can I update my profile?",
        "I want to permanently delete my account, how do I do that?",
        "I received an email about a login from a new device, but it wasn't me.",
        "Can I merge two accounts? I accidentally created a second one.",
        "I'm not receiving the password reset emails.",
        "How do I turn on two-factor authentication for better security?",
        "I lost my phone and can't access my 2FA app. I am locked out.",
        "My account was suspended and I don't know why.",
        "I need to change the default shipping address saved on my profile.",
        "How can I stop receiving marketing emails? Unsubscribing didn't work.",
        "My loyalty points are not showing up in my account dashboard.",
        "I want to upgrade my membership to the premium tier.",
        "Can I pause my subscription for three months?",
        "I need to download a copy of all my data for privacy reasons.",
        "How do I change my billing address on file?",
        "The system says my phone number is already registered to another user.",
        "I've been trying to verify my identity, but my ID upload keeps failing.",
        "How do I change the display name on my public profile?",
        "My account says 'unverified' even though I clicked the email link.",
        "Is there a way to view my entire order history from last year?",
        "I want to downgrade from the Pro plan to the free plan.",
        "My company changed its name, how do I update my business account details?",
        "I keep getting logged out of my account every 5 minutes.",
        "Can I share my premium account with a family member?",
        "Where can I find my account creation date?",
        "I noticed unauthorized charges and I think my account was hacked.",
        "How do I clear my search and browsing history on my account?",
        "My date of birth is wrong on my profile and it won't let me edit it.",
        "I want to revoke access to a third-party app connected to my account.",
        "Can I change my account currency from PKR to USD?",
        "I never received the OTP to verify my new phone number.",
        "Why was my VIP status downgraded to Standard?",
        "I am trying to add a secondary email address to my account.",
        "How do I transfer account ownership to someone else in my company?",
        "I can't find the 'Settings' option on the mobile app.",
        "My account was banned for violating terms, but I haven't done anything wrong!",
        "I want to recover an old account I haven't used in 3 years.",
        "Can you help me unlink my Google account from my profile?",
        "I keep getting an 'Invalid Credentials' error even though my password is correct.",
        "How do I set up a PIN code for faster login?",
        "I want to opt out of data sharing with your third-party partners."
    ]
}

# ============================================================
# EXTRA REAL-WORLD VARIATIONS
# ============================================================

# EXTRA_PHRASES = [
#     "",
#     " Please help me.",
#     " I need an update as soon as possible.",
#     " This is becoming frustrating.",
#     " Can you check this for me?",
#     " I have already contacted support about this.",
#     " Please resolve this issue.",
#     " I have been waiting for a response.",
#     " I need this resolved urgently.",
#     " Can someone look into this?"
# ]
EXTRA_PHRASES = [
    "",
    " Please help me.",
    " I need an update as soon as possible.",
    " This is becoming frustrating.",
    " Can you check this for me?",
    " I have already contacted support about this.",
    " Please resolve this issue.",
    " I have been waiting for a response.",
    " I need this resolved urgently.",
    " Can someone look into this?",
    " Thanks in advance for your help.",
    " I would appreciate a quick reply.",
    " Please get back to me immediately.",
    " This is extremely disappointing.",
    " I expect a resolution by today.",
    " Can I get a callback regarding this?",
    " This is my second time reaching out.",
    " Nobody has replied to my previous emails.",
    " Please escalate this to a manager.",
    " I am really unhappy with this service.",
    " Let me know what information you need from me.",
    " Any updates on this?",
    " This is completely unacceptable.",
    " Please fix this ASAP.",
    " I look forward to hearing from you soon.",
    " Kindly prioritize this ticket.",
    " Why is this taking so long?",
    " I need someone to explain what happened.",
    " This is causing a lot of inconvenience for me.",
    " Can you provide a timeframe for the fix?",
    " I'm losing my patience here.",
    " Please don't send me an automated reply.",
    " I need to speak to a real human agent.",
    " I have attached screenshots for your reference.",
    " This issue is holding up my work.",
    " I expect better customer service than this.",
    " Let me know if there's anything else you need from my side.",
    " What are the next steps?",
    " Please confirm once this is done.",
    " I am considering canceling my account over this.",
    " This issue needs immediate attention.",
    " Can you guide me on how to fix this?",
    " I hope this can be sorted out quickly.",
    " Please investigate this matter deeply.",
    " I am trusting you to resolve this today.",
    " It's been days and still no progress.",
    " Please keep me updated on the status.",
    " I'm really confused and need some clarity.",
    " Could you please point me in the right direction?",
    " Thank you for your time and support."
]
# ============================================================
# DATE GENERATION
# ============================================================

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2026, 8, 28)

date_range = (END_DATE - START_DATE).days

# ============================================================
# CUSTOMER DATA
# ============================================================

customer_ids = [
    f"C{number:05d}"
    for number in range(1, 3001)
]

# Keep customer information consistent
customer_profiles = {}

for customer_id in customer_ids:

    customer_profiles[customer_id] = {
        "customer_type": random.choices(
            CUSTOMER_TYPES,
            weights=[70, 25, 5]
        )[0],

        "previous_complaints": random.choices(
            range(0, 8),
            weights=[35, 25, 15, 10, 6, 4, 3, 2]
        )[0]
    }

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def random_date():
    """
    Generate a random date between START_DATE and END_DATE.
    """
    random_days = random.randint(0, date_range)

    date = START_DATE + timedelta(days=random_days)

    hour = random.randint(8, 22)
    minute = random.randint(0, 59)

    return date.replace(
        hour=hour,
        minute=minute,
        second=0
    )


def generate_order_value(customer_type):
    """
    Generate realistic order value based on customer type.
    """

    if customer_type == "Business":
        return round(random.uniform(30_000, 500_000), 2)

    elif customer_type == "Premium":
        return round(random.uniform(15_000, 200_000), 2)

    else:
        return round(random.uniform(1_000, 80_000), 2)


def create_message(department):
    """
    Create a realistic customer message.
    """

    message = random.choice(
        MESSAGE_TEMPLATES[department]
    )

    # Add realistic variations
    if random.random() < 0.45:
        message += random.choice(EXTRA_PHRASES)

    # Occasionally add informal writing
    if random.random() < 0.08:

        message = message.lower()

    # Occasionally add punctuation
    if random.random() < 0.08:

        message += random.choice([
            "!",
            "!!",
            "???",
            " please!"
        ])

    return message


def generate_status():
    """
    Generate realistic ticket status.
    """

    return random.choices(
        STATUSES,
        weights=[30, 25, 45]
    )[0]


# ============================================================
# GENERATE DATA
# ============================================================

records = []

for i in range(1, NUM_RECORDS + 1):

    ticket_id = f"T{i:06d}"

    customer_id = random.choice(customer_ids)

    profile = customer_profiles[customer_id]

    customer_type = profile["customer_type"]

    previous_complaints = profile["previous_complaints"]

    department = random.choice(DEPARTMENTS)

    message = create_message(department)

    created_at = random_date()

    order_value = generate_order_value(
        customer_type
    )

    status = generate_status()

    record = {
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "message": message,
        "created_at": created_at.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "customer_type": customer_type,
        "order_value": order_value,
        "previous_complaints": previous_complaints,
        "department": department,
        "status": status
    }

    records.append(record)

# ============================================================
# SHUFFLE RECORDS
# ============================================================

random.shuffle(records)

# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# ============================================================
# SAVE CSV
# ============================================================

fieldnames = [
    "ticket_id",
    "customer_id",
    "message",
    "created_at",
    "customer_type",
    "order_value",
    "previous_complaints",
    "department",
    "status"
]

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(records)

# ============================================================
# SUMMARY
# ============================================================

print("=" * 60)
print("CUSTOMER SUPPORT DATASET GENERATED")
print("=" * 60)

print(f"Total Records : {len(records):,}")
print(f"Customers     : {len(customer_ids):,}")
print(f"Output File   : {OUTPUT_FILE}")

print("\nDepartment Distribution:")

department_counts = {}

for record in records:

    department = record["department"]

    department_counts[department] = (
        department_counts.get(department, 0) + 1
    )

for department, count in department_counts.items():

    print(
        f"{department:20} : {count:,}"
    )

print("\nDataset generation completed successfully.")