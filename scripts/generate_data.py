"""
Data Generator for Hiver Support Agent (@AppleSupport)
Generates:
1. data/apple_support_kb.jsonl (Historical Grounding Corpus)
2. data/golden_eval_set_200.jsonl (200 Stratified Ground Truth Test Cases)
"""

import json
import os

KB_ITEMS = [
    # DEVICE_BATTERY_POWER (Historical Apple resolutions)
    {
        "intent": "DEVICE_BATTERY_POWER",
        "sample_query": "My iPhone 14 battery is dying so fast after noon even with light use. What is going on?",
        "resolution_text": "We'd love to help get your battery lasting longer! Take a look at Settings > Battery to see which apps are using the most power. You can also review our tips here: https://support.apple.com/en-us/HT208387. Send us a DM if you're still seeing fast drain.",
        "key_actions": ["check Settings > Battery", "check battery health maximum capacity", "low power mode", "link to HT208387"]
    },
    {
        "intent": "DEVICE_BATTERY_POWER",
        "sample_query": "My iPhone gets extremely hot when charging with the fast charger. Is this normal?",
        "resolution_text": "It's normal for your iPhone to feel slightly warmer while charging, but it shouldn't be uncomfortable to hold. Check that the charging port is free of debris and remove any thick case. If it continues overheating, send us a DM with your iOS version.",
        "key_actions": ["remove case during charging", "check charging port debris", "check ambient temperature"]
    },
    {
        "intent": "DEVICE_BATTERY_POWER",
        "sample_query": "Battery Health dropped to 78% in just 11 months. Does AppleCare cover replacement?",
        "resolution_text": "We can certainly clarify that! If your device is covered by AppleCare+ and battery maximum capacity drops below 80%, you are eligible for a replacement at no extra cost. Schedule a visit at your nearest Apple Store: https://support.apple.com/repair.",
        "key_actions": ["AppleCare+ covers battery under 80%", "Genius Bar reservation"]
    },
    {
        "intent": "DEVICE_BATTERY_POWER",
        "sample_query": "My phone battery percentage jumps from 40% straight to 1% and then shuts down.",
        "resolution_text": "That's certainly unexpected behavior! We recommend restarting your iPhone and ensuring it's updated to the latest iOS. If the sudden drops persist, send us a DM so we can run remote diagnostics on your battery health.",
        "key_actions": ["force restart", "update iOS", "remote diagnostics via DM"]
    },

    # OS_SOFTWARE_UPDATE
    {
        "intent": "OS_SOFTWARE_UPDATE",
        "sample_query": "Updated to iOS 17.4 and now my keyboard lags terribly whenever I type in WhatsApp or Notes.",
        "resolution_text": "Keyboard lag can definitely be frustrating. Try resetting your keyboard dictionary in Settings > General > Transfer or Reset iPhone > Reset > Reset Keyboard Dictionary. Let us know in DM if that resolves the delay!",
        "key_actions": ["Reset Keyboard Dictionary", "Restart device", "Check available storage"]
    },
    {
        "intent": "OS_SOFTWARE_UPDATE",
        "sample_query": "iPhone stuck on Apple logo with the loading bar not moving during update for 3 hours.",
        "resolution_text": "Let's help get your iPhone back up and running! You'll want to place your iPhone into recovery mode by connecting it to a Mac or PC and performing a force restart. Follow these steps: https://support.apple.com/en-us/HT201263.",
        "key_actions": ["Recovery mode force restart", "Connect to Mac/PC Finder or iTunes", "HT201263 guide"]
    },
    {
        "intent": "OS_SOFTWARE_UPDATE",
        "sample_query": "Cannot install update, saying 'Unable to Verify Update - No longer connected to the internet'.",
        "resolution_text": "We understand how annoying that can be. Try going to Settings > General > iPhone Storage, find the downloaded iOS update file, and tap 'Delete Update'. Then restart and download it fresh over Wi-Fi.",
        "key_actions": ["Delete pending update from iPhone Storage", "Switch Wi-Fi network", "Retry download"]
    },
    {
        "intent": "OS_SOFTWARE_UPDATE",
        "sample_query": "Apps keep crashing randomly and closing to the home screen after last night's update.",
        "resolution_text": "We're here to help! Make sure all your apps are updated in the App Store by tapping your profile icon > Update All. If crashes continue, try restarting your iPhone. DM us if specific apps continue crashing.",
        "key_actions": ["Update all apps in App Store", "Force close & restart", "Check free storage"]
    },

    # APPLE_ID_SECURITY
    {
        "intent": "APPLE_ID_SECURITY",
        "sample_query": "I forgot my Apple ID password and my phone number is old. How do I get into my account?",
        "resolution_text": "Account security is our top priority. You can initiate account recovery at https://iforgot.apple.com. Please note this automated security process may take a few days to verify your identity. Never share your verification codes with anyone.",
        "key_actions": ["Use iforgot.apple.com", "Explain account recovery wait period", "Do not share 2FA codes"]
    },
    {
        "intent": "APPLE_ID_SECURITY",
        "sample_query": "Got an email saying my Apple ID was logged in from Russia. I am in the US! Am I hacked?",
        "resolution_text": "That is definitely concerning. First, do not click any links inside that email as it may be phishing. Go directly to https://appleid.apple.com, check your 'Devices' list, and change your password immediately. DM us if you need help securing your account.",
        "key_actions": ["Phishing warning", "Check appleid.apple.com Devices list", "Change password immediately"]
    },
    {
        "intent": "APPLE_ID_SECURITY",
        "sample_query": "My Apple ID is locked for security reasons and won't unlock. Help!",
        "resolution_text": "We know how important your Apple ID is. You can unlock your account by resetting your password at https://iforgot.apple.com. If you still have trouble, reach out to our account security specialists via DM with your region.",
        "key_actions": ["iforgot.apple.com unlock", "Security specialist escalation"]
    },
    {
        "intent": "APPLE_ID_SECURITY",
        "sample_query": "Bought a used iPad from Facebook and it has Activation Lock with the previous owner's email.",
        "resolution_text": "Activation Lock is designed to prevent unauthorized access. Only the original owner can remove this device from their iCloud account at https://icloud.com/find. If you have the original proof of purchase receipt, submit an unlock request: https://support.apple.com/en-us/HT201441.",
        "key_actions": ["Original owner must remove from iCloud", "Original purchase invoice required", "HT201441 link"]
    },

    # HARDWARE_PHYSICAL_DAMAGE
    {
        "intent": "HARDWARE_PHYSICAL_DAMAGE",
        "sample_query": "Dropped my iPhone 15 Pro and the back glass completely shattered. How much does repair cost?",
        "resolution_text": "We're sorry to hear about the drop! Back glass replacement costs vary based on whether you have active AppleCare+ coverage. You can view estimated repair pricing and book a Genius Bar appointment here: https://support.apple.com/repair.",
        "key_actions": ["Check AppleCare+ pricing vs out-of-warranty", "Book Genius Bar at support.apple.com/repair"]
    },
    {
        "intent": "HARDWARE_PHYSICAL_DAMAGE",
        "sample_query": "Dropped my phone in pool water. Speakers sound muffled and crackling. What should I do?",
        "resolution_text": "Do not insert any cables or attempt to charge your phone while it might have moisture. Tap the iPhone gently against your hand with the Lightning/USB-C connector facing down to remove excess liquid, and let it dry in a well-ventilated area for at least 5 hours.",
        "key_actions": ["Do not plug in charger", "Tap gently connector facing down", "Air dry 5 hours, do not use rice"]
    },
    {
        "intent": "HARDWARE_PHYSICAL_DAMAGE",
        "sample_query": "Power button is physically stuck and clicking does nothing. Need a repair technician.",
        "resolution_text": "A jammed hardware button requires in-person service by an Apple Authorized Service Provider. Let's get you set up with an appointment. Please visit https://locate.apple.com to find your nearest authorized repair center.",
        "key_actions": ["locate.apple.com for service center", "Genius Bar appointment", "Hardware escalation"]
    },

    # SUBSCRIPTION_BILLING
    {
        "intent": "SUBSCRIPTION_BILLING",
        "sample_query": "Apple just billed my card $14.99 and I have no idea what it's for. I want my money back!",
        "resolution_text": "We understand unexpected charges are frustrating! You can review your complete purchase history and request a refund by signing in at https://reportaproblem.apple.com. You can also view active subscriptions in Settings > [Your Name] > Subscriptions.",
        "key_actions": ["reportaproblem.apple.com for refund", "Settings > Name > Subscriptions to cancel"]
    },
    {
        "intent": "SUBSCRIPTION_BILLING",
        "sample_query": "My 8 year old accidentally spent $80 on Roblox coins without my permission. Can I get a refund?",
        "resolution_text": "We definitely want to help with accidental purchases. Please head to https://reportaproblem.apple.com, sign in with your Apple ID, select 'Request a refund', and choose 'A child made purchases without permission'. Also check Screen Time settings to set purchase restrictions.",
        "key_actions": ["reportaproblem.apple.com refund request", "Screen Time in-app purchase restrictions"]
    },
    {
        "intent": "SUBSCRIPTION_BILLING",
        "sample_query": "Canceled Tinder subscription last month but Apple charged me again yesterday. Fix this now!",
        "resolution_text": "We'd be glad to look into this recurring charge. Confirm the cancellation in Settings > [Your Name] > Subscriptions. If it shows expired yet you were billed, please request a refund at https://reportaproblem.apple.com and DM us your transaction ID.",
        "key_actions": ["Verify subscription status in Settings", "Request refund at reportaproblem.apple.com", "DM transaction ID"]
    },

    # CONNECTIVITY_ACCESSORIES
    {
        "intent": "CONNECTIVITY_ACCESSORIES",
        "sample_query": "Left AirPod has no sound at all even though both are charged at 100%.",
        "resolution_text": "Let's get both AirPods playing clearly again! Place both AirPods in the charging case, keep the lid open, and press and hold the setup button on the back for 15 seconds until the status light flashes amber then white. Check the steps here: https://support.apple.com/en-us/HT209463.",
        "key_actions": ["Reset AirPods with 15s case button hold", "Clean speaker mesh", "HT209463 reset guide"]
    },
    {
        "intent": "CONNECTIVITY_ACCESSORIES",
        "sample_query": "Wi-Fi toggle in Settings is greyed out and cannot be turned on. Bluetooth also failing.",
        "resolution_text": "A greyed-out Wi-Fi toggle can sometimes indicate hardware modem issues. First, try Settings > General > Transfer or Reset iPhone > Reset > Reset Network Settings. If it remains greyed out after restart, hardware inspection at a Genius Bar is required.",
        "key_actions": ["Reset Network Settings", "Force restart", "If persistent, hardware repair required"]
    },
    {
        "intent": "CONNECTIVITY_ACCESSORIES",
        "sample_query": "CarPlay keeps disconnecting every 5 minutes while driving. Using original Apple cable.",
        "resolution_text": "We know how inconvenient CarPlay disconnects can be. Try going to Settings > General > CarPlay, select your car, and tap 'Forget This Car', then reconnect. Also inspect your Lightning/USB-C port for any pocket lint with a non-conductive tool.",
        "key_actions": ["Forget This Car in CarPlay settings", "Inspect port for lint", "Check vehicle infotainment firmware update"]
    },
    {
        "intent": "CONNECTIVITY_ACCESSORIES",
        "sample_query": "Apple Watch won't pair with new iPhone 15. Says 'Pairing Failed' every time.",
        "resolution_text": "Let's help get your Apple Watch synced up! On the watch, go to Settings > General > Reset > Erase All Content and Settings. Ensure both devices have Bluetooth and Wi-Fi turned on, then try pairing again via the Apple Watch app on your iPhone.",
        "key_actions": ["Erase all content & settings on Apple Watch", "Bluetooth & Wi-Fi on", "Re-pair via Watch app"]
    }
]

def generate_golden_dataset():
    """
    Builds a stratified 200-sample golden evaluation set.
    Strata:
    1. DEVICE_BATTERY_POWER: 35 samples (Auto: 25, Escalate: 10)
    2. OS_SOFTWARE_UPDATE: 35 samples (Auto: 25, Escalate: 10)
    3. APPLE_ID_SECURITY: 35 samples (Auto: 10, Escalate: 25)
    4. HARDWARE_PHYSICAL_DAMAGE: 30 samples (Auto: 0, Escalate: 30 - 100% escalation)
    5. SUBSCRIPTION_BILLING: 35 samples (Auto: 22, Escalate: 13)
    6. CONNECTIVITY_ACCESSORIES: 30 samples (Auto: 23, Escalate: 7)
    Total = 200 samples.
    """
    
    samples = []
    
    # Stratum 1: Battery & Power (35)
    battery_cases = [
        # Auto-handle (25)
        ("My 13 Pro battery drains 20% in an hour on iOS 17.1. Anything I can toggle to save juice?", "DEVICE_BATTERY_POWER", False, "Standard battery drain query resolvable with Low Power Mode and battery optimization tips.", "SIMPLE", 5),
        ("Battery health is 84% after 2 years. Should I replace it or is this normal?", "DEVICE_BATTERY_POWER", False, "Normal battery degradation consultation resolvable via standard advisory.", "SIMPLE", 5),
        ("Is it safe to charge iPhone overnight with optimized battery charging turned on?", "DEVICE_BATTERY_POWER", False, "Informational feature query easily answered with official knowledge.", "SIMPLE", 5),
        ("phone gets warm when playing pubg mobile while charging... normal?", "DEVICE_BATTERY_POWER", False, "Expected thermal behavior under heavy gaming + charging workload.", "SIMPLE", 4),
        ("Why does my battery percentage stay at 80% for so long when plugged in overnight?", "DEVICE_BATTERY_POWER", False, "Optimized Battery Charging explanation required.", "SIMPLE", 5),
        ("What's the best wattage charger to use for iPhone 15? 20W or 30W?", "DEVICE_BATTERY_POWER", False, "Hardware specification advisory auto-resolvable.", "SIMPLE", 5),
        ("Safari is taking 45% of my battery background activity today, how do I stop it?", "DEVICE_BATTERY_POWER", False, "Background app refresh and tab management settings troubleshooting.", "MODERATE", 5),
        ("ios 17.2 battery life is completely terrible apple please fix this trash update", "DEVICE_BATTERY_POWER", False, "Venting customer but routine post-update re-indexing advice applies.", "MODERATE", 4),
        ("My phone charges to 100% but drops to 90% within 10 minutes of unplugging.", "DEVICE_BATTERY_POWER", False, "Diagnostic advice and battery calibration check guidance.", "MODERATE", 4),
        ("Is fast charging damaging my iPhone battery health faster than slow charging?", "DEVICE_BATTERY_POWER", False, "Technical advice query on fast charging thermal dynamics.", "SIMPLE", 5),
        ("MagSafe charger is charging very slowly, takes 4 hours for full charge.", "DEVICE_BATTERY_POWER", False, "Troubleshooting power adapter wattage requirements for MagSafe (20W+).", "MODERATE", 5),
        ("Clean energy charging feature keeps pausing my charge at night. How to disable?", "DEVICE_BATTERY_POWER", False, "Settings navigation guidance for Clean Energy Charging toggle.", "SIMPLE", 5),
        ("Screen on time is only 3 hours on my iPhone 12 mini. Any tips?", "DEVICE_BATTERY_POWER", False, "Standard battery preservation recommendations.", "SIMPLE", 4),
        ("Battery health maximum capacity dropped from 100% to 98% in two weeks. Am I doing something wrong?", "DEVICE_BATTERY_POWER", False, "Reassurance regarding non-linear battery estimation algorithms.", "SIMPLE", 5),
        ("Can I use an iPad 30W USB-C brick to charge my iPhone 13?", "DEVICE_BATTERY_POWER", False, "Compatibility confirmation regarding USB-PD power negotiation.", "SIMPLE", 5),
        ("My phone won't charge past 80% even when Clean Energy Charging is turned off.", "DEVICE_BATTERY_POWER", False, "Explain 80% Limit feature on iPhone 15 or thermal pause.", "MODERATE", 5),
        ("Why does Low Power Mode turn off automatically at 80%?", "DEVICE_BATTERY_POWER", False, "Expected iOS system design clarification.", "SIMPLE", 5),
        ("Does dark mode actually save battery on an OLED screen?", "DEVICE_BATTERY_POWER", False, "Accurate display technology guidance.", "SIMPLE", 5),
        ("My battery icon turned yellow. What does that mean?", "DEVICE_BATTERY_POWER", False, "Low Power Mode indicator explanation.", "SIMPLE", 5),
        ("Apps like Instagram are chewing through my battery even when closed.", "DEVICE_BATTERY_POWER", False, "Guidance on disabling Background App Refresh.", "SIMPLE", 4),
        ("Phone is charging in reverse? Plugged it in at 15% and now it says 12%!", "DEVICE_BATTERY_POWER", False, "Faulty cable/low-amperage port troubleshooting.", "MODERATE", 4),
        ("Is third party Anker wireless charging pad certified and safe for iPhone?", "DEVICE_BATTERY_POWER", False, "Qi certification advisory.", "SIMPLE", 5),
        ("How to see individual app battery consumption over the last 10 days?", "DEVICE_BATTERY_POWER", False, "Settings navigation instruction.", "SIMPLE", 5),
        ("Phone says 'Charging on hold due to iPhone temperature'. Should I be worried?", "DEVICE_BATTERY_POWER", False, "Thermal protection safeguard explanation.", "SIMPLE", 5),
        ("Will keeping my phone plugged in all day at my desk ruin the battery?", "DEVICE_BATTERY_POWER", False, "Power management controller behavior explanation.", "SIMPLE", 5),

        # Escalate (10)
        ("URGENT: My iPhone battery has physically swollen and the screen is popping off the frame!", "DEVICE_BATTERY_POWER", True, "Hazardous battery swelling poses serious fire risk; immediate human safety intervention required.", "HOSTILE_EMERGENCY", 5),
        ("My lightning charging port started sparking and smoking while plugged in! There's a burnt plastic smell.", "DEVICE_BATTERY_POWER", True, "Hardware thermal event / electrical hazard; requires immediate incident intake.", "HOSTILE_EMERGENCY", 5),
        ("Battery dropped to 72% within 6 months. Battery Settings says 'Service Required'. I have AppleCare+.", "DEVICE_BATTERY_POWER", True, "Hardware defect triggering service warning within warranty; requires authorized repair booking.", "MODERATE", 5),
        ("Phone is boiling hot to touch, too hot to hold, and displays temperature warning even when idle.", "DEVICE_BATTERY_POWER", True, "Severe thermal runaway risk requiring hardware diagnostic specialist.", "MODERATE", 4),
        ("My brand new iPhone 15 Pro won't turn on at all. Hard reset does nothing, completely dead on day 2.", "DEVICE_BATTERY_POWER", True, "Dead on arrival (DOA) hardware failure requiring DOA exchange/human claim.", "MODERATE", 5),
        ("iPhone shuts down abruptly at 50% battery every single day. Restored iOS twice, problem still happens.", "DEVICE_BATTERY_POWER", True, "Persistent hardware logic board/battery failure unresolved by full software restore.", "MODERATE", 4),
        ("Third party battery replacement message 'Unknown Part' won't go away and phone restarts every 3 mins.", "DEVICE_BATTERY_POWER", True, "Panic log / watchdog timeout crash from non-genuine or faulty hardware part.", "AMBIGUOUS_EDGE_CASE", 4),
        ("Left my iPhone on charger overnight and woke up with the back glass scorched and brown discoloration.", "DEVICE_BATTERY_POWER", True, "Safety incident report required for heat damage to enclosure.", "HOSTILE_EMERGENCY", 5),
        ("Battery health dropped 15% in 3 days following an Apple Store repair. Technician messed up my phone!", "DEVICE_BATTERY_POWER", True, "Service complaint / technician error dispute requiring store manager escalation.", "HOSTILE_EMERGENCY", 4),
        ("Phone vibrates continuously and won't accept charge from 5 different verified Apple cables.", "DEVICE_BATTERY_POWER", True, "Physical Tristar/charging IC hardware failure on motherboard.", "MODERATE", 4)
    ]

    # Stratum 2: OS & Software Update (35)
    os_cases = [
        # Auto-handle (25)
        ("Updated to iOS 17.3 and my home screen widgets went blank black squares. How to fix?", "OS_SOFTWARE_UPDATE", False, "Widget cache reset via device restart or re-adding widget.", "SIMPLE", 5),
        ("Cannot update because it says 'Not Enough Space'. How do I clear system data?", "OS_SOFTWARE_UPDATE", False, "Storage management troubleshooting and temporary app offloading.", "SIMPLE", 5),
        ("How do I downgrade back to iOS 16 from iOS 17? The new layout is confusing.", "OS_SOFTWARE_UPDATE", False, "Explain Apple's signed IPSW policy and lack of official downgrade support.", "MODERATE", 4),
        ("FaceID not working immediately after software update, says 'Move iPhone lower'.", "OS_SOFTWARE_UPDATE", False, "Camera sensor cleaning and Face ID reset guidance.", "MODERATE", 4),
        ("My camera app is black when I open it. Started after the security patch.", "OS_SOFTWARE_UPDATE", False, "App force kill, camera privacy permissions, and restart troubleshooting.", "MODERATE", 4),
        ("How to turn off automatic overnight iOS updates? I want to choose when to update.", "OS_SOFTWARE_UPDATE", False, "Settings > General > Software Update > Automatic Updates toggle.", "SIMPLE", 5),
        ("Siri sounds robotic and distorted after the latest update.", "OS_SOFTWARE_UPDATE", False, "Siri voice re-download guidance in Settings.", "SIMPLE", 5),
        ("Where did the call end button move in iOS 17? Keep pressing wrong spot.", "OS_SOFTWARE_UPDATE", False, "User interface change explanation and layout options.", "SIMPLE", 5),
        ("Notifications are not making any sound since updating yesterday.", "OS_SOFTWARE_UPDATE", False, "Focus mode / Do Not Disturb audit and Sound settings review.", "SIMPLE", 5),
        ("How long does an iOS 17 update usually take to prepare and install?", "OS_SOFTWARE_UPDATE", False, "General time estimation advisory (15-45 mins depending on bandwidth).", "SIMPLE", 5),
        ("Airdrop NameDrop feature keeps popping up when phones touch. How do I disable?", "OS_SOFTWARE_UPDATE", False, "Settings > General > AirDrop > Bringing Devices Together toggle.", "SIMPLE", 5),
        ("Lock screen clock font is huge and bold. How to change it back?", "OS_SOFTWARE_UPDATE", False, "Lock screen customization gesture instructions.", "SIMPLE", 5),
        ("Downloaded update says 'Pause' and won't resume on cellular data.", "OS_SOFTWARE_UPDATE", False, "Clarify cellular download size limitations or low data mode.", "SIMPLE", 5),
        ("Safari tabs rearranged themselves into tab groups. How to revert to regular grid?", "OS_SOFTWARE_UPDATE", False, "Safari layout preference instructions.", "SIMPLE", 5),
        ("Screen brightness keeps dimming randomly even though auto-brightness is off.", "OS_SOFTWARE_UPDATE", False, "Explain thermal throttling or True Tone / Night Shift interference.", "MODERATE", 4),
        ("Voicemail tab in Phone app is completely blank after carrier settings update.", "OS_SOFTWARE_UPDATE", False, "Carrier voicemail reset and network reboot instructions.", "MODERATE", 4),
        ("Spotlight search is sluggish and takes 5 seconds to find contacts post update.", "OS_SOFTWARE_UPDATE", False, "Explain background spotlight indexing post-update; suggest restart.", "SIMPLE", 5),
        ("How do I create a sticker from a photo on iOS 17?", "OS_SOFTWARE_UPDATE", False, "Step-by-step feature guidance for Photo subject lifting.", "SIMPLE", 5),
        ("Is it safe to install the iOS public beta on my primary work phone?", "OS_SOFTWARE_UPDATE", False, "Standard beta cautionary advice and backup recommendation.", "SIMPLE", 5),
        ("Photos app says 'Curating best photos / Finding duplicates - plug in to power'.", "OS_SOFTWARE_UPDATE", False, "Explain machine learning indexing requires overnight charging.", "SIMPLE", 5),
        ("Haptic feedback on keyboard disappeared after the update.", "OS_SOFTWARE_UPDATE", False, "Settings > Sounds & Haptics > Keyboard Feedback navigation.", "SIMPLE", 5),
        ("Can't find the iTunes Store app anymore, did iOS delete it?", "OS_SOFTWARE_UPDATE", False, "App Library search and App Store re-download guide.", "SIMPLE", 5),
        ("StandBy mode clock doesn't turn red at night on my nightstand.", "OS_SOFTWARE_UPDATE", False, "Settings > StandBy > Night Mode toggle guidance.", "SIMPLE", 5),
        ("Live Voicemail isn't showing transcripts when people call.", "OS_SOFTWARE_UPDATE", False, "Language/Region availability and feature settings check.", "SIMPLE", 5),
        ("What does the orange dot at the top of my screen mean after updating?", "OS_SOFTWARE_UPDATE", False, "Microphone privacy indicator explanation.", "SIMPLE", 5),

        # Escalate (10)
        ("HELP! My iPad is stuck in an infinite bootloop showing the Apple logo then black screen forever!", "OS_SOFTWARE_UPDATE", True, "Infinite bootloop unrecoverable via basic restart; requires DFU recovery or hardware diagnostic.", "MODERATE", 5),
        ("Update failed mid-way and now screen displays 'support.apple.com/iphone/restore'. iTunes throws Error 4013.", "OS_SOFTWARE_UPDATE", True, "NAND/baseband hardware flash error during restore; requires technician repair.", "MODERATE", 5),
        ("iOS update corrupted all my local notes and family photos! I need a data recovery specialist NOW.", "OS_SOFTWARE_UPDATE", True, "Critical data loss incident with high distress; needs senior technical advisor.", "HOSTILE_EMERGENCY", 4),
        ("Your update completely bricked my $1200 iPhone 14 Pro. Won't respond to buttons or PC. I demand a replacement!", "OS_SOFTWARE_UPDATE", True, "Bricked device claim with hostile legal/replacement demand.", "HOSTILE_EMERGENCY", 5),
        ("MacBook Pro went black during macOS Sonoma update and fans are running at 100% full blast with no display.", "OS_SOFTWARE_UPDATE", True, "Firmware/SMC/T2 chip crash requiring Apple Configurator DFU revive.", "MODERATE", 5),
        ("After updating to iOS 17.4, cellular shows 'Error - An update is required to use cellular data'.", "OS_SOFTWARE_UPDATE", True, "Known cellular baseband modem hardware failure; requires device replacement.", "MODERATE", 5),
        ("Every time I unlock my phone the entire springboard crashes and resprings in a loop. Cannot access settings.", "OS_SOFTWARE_UPDATE", True, "Critical UI springboard crash loop preventing user input.", "MODERATE", 4),
        ("My company MDM profile locked my phone into single app mode and won't let me update or wipe.", "OS_SOFTWARE_UPDATE", True, "Enterprise MDM policy restriction requiring corporate admin or Tier-2 support.", "AMBIGUOUS_EDGE_CASE", 4),
        ("Update wiped my eSIM profile and now I have zero cell service and cannot contact my bank.", "OS_SOFTWARE_UPDATE", True, "Carrier profile corruption leaving user stranded without emergency comms.", "HOSTILE_EMERGENCY", 4),
        ("Screen is completely frozen on 'Swipe up to upgrade' and touch screen does not respond to touch.", "OS_SOFTWARE_UPDATE", True, "Digitizer driver failure or frozen touch controller during post-install setup.", "MODERATE", 4)
    ]

    # Stratum 3: Apple ID & Security (35)
    security_cases = [
        # Auto-handle (10)
        ("Forgot my Apple ID password. Where do I go to reset it?", "APPLE_ID_SECURITY", False, "Standard self-service redirect to iforgot.apple.com.", "SIMPLE", 5),
        ("How do I change the trusted phone number on my Apple ID account?", "APPLE_ID_SECURITY", False, "Self-service settings guidance in Settings > Apple ID > Sign-In & Security.", "SIMPLE", 5),
        ("What is an Apple ID Recovery Key and how do I create one?", "APPLE_ID_SECURITY", False, "Informational guidance on security feature and trade-offs.", "SIMPLE", 5),
        ("How can I see all devices currently logged into my iCloud account?", "APPLE_ID_SECURITY", False, "Settings navigation to device list at appleid.apple.com.", "SIMPLE", 5),
        ("Can I merge two different Apple IDs into a single account?", "APPLE_ID_SECURITY", False, "Explain Apple's policy on non-mergeable Apple IDs.", "SIMPLE", 5),
        ("I got a new SIM card. How do I update my iMessage phone number?", "APPLE_ID_SECURITY", False, "Settings > Messages > Send & Receive troubleshooting.", "SIMPLE", 5),
        ("How do I set up a Legacy Contact for my Apple ID in case something happens to me?", "APPLE_ID_SECURITY", False, "Step-by-step guidance on Digital Legacy setup.", "SIMPLE", 5),
        ("What is Hide My Email and how does it work with Sign in with Apple?", "APPLE_ID_SECURITY", False, "Feature explanation for iCloud+ privacy tool.", "SIMPLE", 5),
        ("Can I transfer an App Store purchase to my secondary Apple ID?", "APPLE_ID_SECURITY", False, "Clarify license binding to Apple ID; recommend Family Sharing.", "SIMPLE", 5),
        ("How do I turn off Two-Factor Authentication? I don't want it.", "APPLE_ID_SECURITY", False, "Explain mandatory 2FA policy for Apple ID security.", "SIMPLE", 5),

        # Escalate (25)
        ("MY ACCOUNT WAS HACKED! Someone changed my Apple ID email, removed my trusted phone number, and locked my phone!", "APPLE_ID_SECURITY", True, "Hostile account takeover; unauthorized credential modification requires emergency fraud escalation.", "HOSTILE_EMERGENCY", 5),
        ("Someone is blackmaling me using Find My on my MacBook and demanded $500 Bitcoin to unlock it!", "APPLE_ID_SECURITY", True, "Extortion/criminal activity and compromised iCloud credentials; urgent human escalation.", "HOSTILE_EMERGENCY", 5),
        ("I clicked a fake SMS link pretending to be USPS and typed my Apple ID password and 2FA code. What now??", "APPLE_ID_SECURITY", True, "Active phishing breach with credential compromise; urgent account lockdown required.", "HOSTILE_EMERGENCY", 5),
        ("Account recovery at iforgot.apple.com says waiting 28 days but all my business data is locked out!", "APPLE_ID_SECURITY", True, "High-friction account recovery dispute requiring manual identity review evaluation.", "MODERATE", 4),
        ("My deceased father's iPhone is locked. We have court probate documents and death certificate to unlock.", "APPLE_ID_SECURITY", True, "Legal probate case requiring Apple Legal and specialized documentation review.", "AMBIGUOUS_EDGE_CASE", 5),
        ("A stalker is tracking my location through an unknown AirTag that keeps following me home. Call police?", "APPLE_ID_SECURITY", True, "Physical safety and domestic stalking risk; immediate human protocol and law enforcement guidance.", "HOSTILE_EMERGENCY", 5),
        ("My child accidentally locked themselves out of their iPad with passcode and there's no computer available.", "APPLE_ID_SECURITY", True, "Requires alternate verification or Apple Store appointment booking.", "MODERATE", 4),
        ("I received 15 two-factor authentication prompts in 2 minutes while sleeping. Someone is brute-forcing my account!", "APPLE_ID_SECURITY", True, "MFA fatigue/push bombing attack in progress; security team alert.", "HOSTILE_EMERGENCY", 5),
        ("Find My shows my stolen iPhone in another city. Can Apple support remotely wipe it for me?", "APPLE_ID_SECURITY", True, "Theft incident requiring stolen device protocol guidance and remote wipe verification.", "MODERATE", 4),
        ("Someone added an unauthorized credit card to my Apple Wallet and bought electronics!", "APPLE_ID_SECURITY", True, "Financial identity theft and unauthorized Apple Pay provisioning.", "HOSTILE_EMERGENCY", 5),
        ("Bought this iPhone on eBay and Activation Lock is tied to an unknown email. Seller deleted their account!", "APPLE_ID_SECURITY", True, "Activation Lock bypass request without original owner credentials; strict policy review.", "MODERATE", 5),
        ("Lost my Recovery Key AND forgot my password. Apple website says account is permanently lost. Is there any way?", "APPLE_ID_SECURITY", True, "Permanent lockout edge case requiring senior tier confirmation of cryptographic policy.", "AMBIGUOUS_EDGE_CASE", 4),
        ("Someone ported my phone number (SIM swap) and reset my Apple ID password!", "APPLE_ID_SECURITY", True, "Targeted SIM swap attack compromising identity infrastructure.", "HOSTILE_EMERGENCY", 5),
        ("Apple ID says 'Account has been disabled in the App Store and iTunes'. Cannot download any apps.", "APPLE_ID_SECURITY", True, "Account administrative hold by risk/fraud team requiring internal agent unblock.", "MODERATE", 5),
        ("My ex-partner is monitoring my messages through shared Apple ID. How do I secretly remove their access?", "APPLE_ID_SECURITY", True, "Safety Check / domestic privacy crisis requiring discreet, sensitive handling.", "HOSTILE_EMERGENCY", 5),
        ("Received an email receipt for a $400 purchase on an iPhone 16 in Brazil. I don't own an iPhone 16!", "APPLE_ID_SECURITY", True, "Fraudulent device addition and unauthorized transaction.", "HOSTILE_EMERGENCY", 5),
        ("Security keys feature locked me out after one of my YubiKeys was lost during travel.", "APPLE_ID_SECURITY", True, "Hardware security key failure requiring specialized FIDO key recovery advice.", "MODERATE", 4),
        ("Someone set up Screen Time passcode on my phone as a prank and now I can't delete apps or change settings.", "APPLE_ID_SECURITY", True, "Screen time lockout requiring passcode recovery or wipe assistance.", "MODERATE", 4),
        ("Can Apple unlock this phone for local police department? We have a search warrant.", "APPLE_ID_SECURITY", True, "Law enforcement inquiry requiring Apple Legal Law Enforcement portal redirection.", "AMBIGUOUS_EDGE_CASE", 5),
        ("Two-factor code is sending to my stolen phone that I no longer have access to.", "APPLE_ID_SECURITY", True, "Catch-22 MFA barrier requiring account recovery workflow management.", "MODERATE", 4),
        ("My Apple ID email domain expired and someone bought the domain and is intercepting my reset emails!", "APPLE_ID_SECURITY", True, "Domain hijacking leading to account security vulnerability.", "AMBIGUOUS_EDGE_CASE", 4),
        ("I keep getting signed out of iCloud across all my devices every 10 minutes.", "APPLE_ID_SECURITY", True, "Anomalous token invalidation suggesting security session revocation.", "MODERATE", 4),
        ("Someone created an iCloud account using my corporate email address without my consent.", "APPLE_ID_SECURITY", True, "Corporate identity dispute / unauthorized enterprise domain usage.", "AMBIGUOUS_EDGE_CASE", 4),
        ("A pop-up on Safari said 'Apple Security: Pegasus Spyware Detected - Call 1-800...' Is this real?", "APPLE_ID_SECURITY", True, "Tech support scam scareware; verify safety and reassure user.", "MODERATE", 4),
        ("Account recovery was cancelled because someone accessed my old iPad. I think the burglar is using it!", "APPLE_ID_SECURITY", True, "Active burglary/theft interference with account recovery.", "HOSTILE_EMERGENCY", 5)
    ]

    # Stratum 4: Hardware Physical Damage (30) - All 30 are ESCALATE
    damage_cases = [
        ("Dropped my iPhone 14 in the toilet. Now sound is garbled and camera lens has moisture fog.", "HARDWARE_PHYSICAL_DAMAGE", True, "Liquid ingress and camera fogging requires hardware assessment; cannot fix via software.", "MODERATE", 5),
        ("Sat on my iPad Pro and the aluminum chassis is visibly bent like a banana.", "HARDWARE_PHYSICAL_DAMAGE", True, "Structural frame damage compromising battery integrity; physical replacement needed.", "MODERATE", 5),
        ("Shattered front screen glass into small sharp pieces. Can I just put tape over it?", "HARDWARE_PHYSICAL_DAMAGE", True, "Safety hazard from broken glass; requires display assembly replacement.", "MODERATE", 5),
        ("Green vertical line running down the entire OLED screen after dropping the phone on carpet.", "HARDWARE_PHYSICAL_DAMAGE", True, "OLED panel controller / flex cable hardware defect; needs display swap.", "MODERATE", 5),
        ("Dropped my Apple Watch Ultra rock climbing and sapphire crystal has a deep crack.", "HARDWARE_PHYSICAL_DAMAGE", True, "Compromised water resistance seal and cracked crystal requires service unit.", "MODERATE", 5),
        ("A child shoved a coin into the USB-C port and bent the inner pins.", "HARDWARE_PHYSICAL_DAMAGE", True, "Physical connector pin damage; electrical short hazard.", "MODERATE", 5),
        ("MacBook screen has purple ink-like bleed expanding across the corner.", "HARDWARE_PHYSICAL_DAMAGE", True, "Liquid crystal leakage from internal display impact.", "MODERATE", 5),
        ("Ear speaker on iPhone 13 is barely audible during phone calls even at max volume.", "HARDWARE_PHYSICAL_DAMAGE", True, "Physical receiver mesh blockage or blown speaker transducer.", "MODERATE", 4),
        ("Camera clicks violently and buzzes whenever I open the camera app. Optical image stabilization broken.", "HARDWARE_PHYSICAL_DAMAGE", True, "Physical OIS gyroscope failure; requires camera module replacement.", "MODERATE", 5),
        ("Face ID hardware failure message: 'A problem was detected with the TrueDepth Camera'.", "HARDWARE_PHYSICAL_DAMAGE", True, "TrueDepth infrared hardware failure; requires technician recalibration.", "MODERATE", 5),
        ("iPhone back camera glass circle shattered while in my pocket. Lens is exposed to dust.", "HARDWARE_PHYSICAL_DAMAGE", True, "Sapphire camera lens fracture; requires module repair.", "MODERATE", 5),
        ("Coffee spilled over my MacBook Air keyboard. Now spacebar and trackpad don't click.", "HARDWARE_PHYSICAL_DAMAGE", True, "Liquid damage affecting membrane switches and logic board.", "MODERATE", 5),
        ("Mute switch on side of phone broke off completely and fell out.", "HARDWARE_PHYSICAL_DAMAGE", True, "Missing physical toggle button; chassis repair needed.", "SIMPLE", 5),
        ("AirPods Pro crackles and makes static popping sound when I walk or chew.", "HARDWARE_PHYSICAL_DAMAGE", True, "Known AirPods Pro acoustic mesh hardware failure eligible for service program.", "MODERATE", 5),
        ("Dog chewed on Apple Pencil tip and damaged the internal sensor.", "HARDWARE_PHYSICAL_DAMAGE", True, "Physical damage to pressure transducer; accessory replacement needed.", "SIMPLE", 5),
        ("iPhone fell off a motorcycle at 50mph. Completely obliterated into 3 pieces.", "HARDWARE_PHYSICAL_DAMAGE", True, "Catastrophic damage claim for out-of-warranty replacement.", "HOSTILE_EMERGENCY", 5),
        ("Top half of touch screen does not register any touch input after a drop.", "HARDWARE_PHYSICAL_DAMAGE", True, "Digitizer hardware separation or broken touch bus.", "MODERATE", 5),
        ("MacBook trackpad haptic click is no longer clicking at all.", "HARDWARE_PHYSICAL_DAMAGE", True, "Force Touch haptic engine or swollen battery pressing against trackpad.", "MODERATE", 4),
        ("Dropped iPhone in saltwater ocean. Washed with tap water. Will it survive?", "HARDWARE_PHYSICAL_DAMAGE", True, "Corrosive saltwater intrusion; urgent service inspection advised.", "MODERATE", 5),
        ("iPhone volume up button is permanently pressed in and volume slider won't move.", "HARDWARE_PHYSICAL_DAMAGE", True, "Stuck tactile switch mechanism.", "MODERATE", 4),
        ("SIM card tray won't eject even when pressing the pin hard into the hole.", "HARDWARE_PHYSICAL_DAMAGE", True, "Jammed internal ejector lever; requires repair specialist.", "SIMPLE", 5),
        ("Flashlight / rear LED flash stopped working completely. Flash icon is disabled.", "HARDWARE_PHYSICAL_DAMAGE", True, "Rear flash flex cable or hardware sensor fault.", "MODERATE", 4),
        ("Speaker emits loud screeching feedback noise whenever a call connects.", "HARDWARE_PHYSICAL_DAMAGE", True, "Audio codec chip or speaker amplifier hardware issue.", "MODERATE", 4),
        ("Dropped phone and now vibration feels like a loose rattle inside the phone.", "HARDWARE_PHYSICAL_DAMAGE", True, "Taptic Engine mounting screw sheared or defective motor.", "MODERATE", 5),
        ("Car ran over my AirPods case. Lid is detached and hinges are broken.", "HARDWARE_PHYSICAL_DAMAGE", True, "Severe physical crushing; replacement case required.", "SIMPLE", 5),
        ("Dead pixels cluster spreading in center of iPad display.", "HARDWARE_PHYSICAL_DAMAGE", True, "Panel manufacturing defect or internal pressure crack.", "MODERATE", 4),
        ("Headphone jack adapter broke off inside the port and the metal tip is stuck.", "HARDWARE_PHYSICAL_DAMAGE", True, "Foreign object lodged in port requiring specialized extraction tool.", "SIMPLE", 5),
        ("Display is lifting away from the side frame with visible light leak.", "HARDWARE_PHYSICAL_DAMAGE", True, "Adhesive failure or internal battery expansion pushing screen out.", "MODERATE", 5),
        ("My iPhone was in a house fire. Enclosure is melted. Can Apple retrieve my files from memory chip?", "HARDWARE_PHYSICAL_DAMAGE", True, "Severe fire damage inquiry requiring specialized board-level recovery advice.", "HOSTILE_EMERGENCY", 4),
        ("Water indicator inside SIM tray is bright red. Does this void standard warranty?", "HARDWARE_PHYSICAL_DAMAGE", True, "Liquid Contact Indicator (LCI) warranty dispute requiring human policy explanation.", "MODERATE", 5)
    ]

    # Stratum 5: Subscription & Billing (35)
    billing_cases = [
        # Auto-handle (22)
        ("Where can I see what subscriptions are currently renewing on my Apple account?", "SUBSCRIPTION_BILLING", False, "Standard navigation to Settings > [Name] > Subscriptions.", "SIMPLE", 5),
        ("How do I cancel Apple Music before the free 3-month trial ends?", "SUBSCRIPTION_BILLING", False, "Cancellation steps provided for free trial self-service.", "SIMPLE", 5),
        ("How can I request a refund for an app my child bought accidentally?", "SUBSCRIPTION_BILLING", False, "Direct customer to reportaproblem.apple.com with instructions.", "SIMPLE", 5),
        ("Can I pay for iCloud+ storage with Apple Gift Card balance?", "SUBSCRIPTION_BILLING", False, "Payment hierarchy explanation (Apple ID balance used first).", "SIMPLE", 5),
        ("Why does Apple charge $0.99 every month? What is that?", "SUBSCRIPTION_BILLING", False, "Explain common 50GB iCloud storage plan price point.", "SIMPLE", 5),
        ("How to change the default credit card used for Apple Pay and App Store?", "SUBSCRIPTION_BILLING", False, "Wallet & Apple Pay settings navigation guide.", "SIMPLE", 5),
        ("Can I share my Apple One subscription with 4 family members?", "SUBSCRIPTION_BILLING", False, "Family Sharing plan details explanation.", "SIMPLE", 5),
        ("How do I download tax invoice/receipt for my App Store purchase?", "SUBSCRIPTION_BILLING", False, "Purchase history and email receipt resend guidance.", "SIMPLE", 5),
        ("What happens to my photos if I downgrade iCloud storage from 2TB to 200GB?", "SUBSCRIPTION_BILLING", False, "Storage over-quota grace period policy explanation.", "SIMPLE", 5),
        ("Does canceling a subscription give me an immediate pro-rated refund?", "SUBSCRIPTION_BILLING", False, "Explain access remains until end of billing cycle unless refund requested.", "SIMPLE", 5),
        ("How do I turn off Family Sharing purchase sharing so everyone pays for their own apps?", "SUBSCRIPTION_BILLING", False, "Settings > Family > Purchase Sharing toggle guide.", "SIMPLE", 5),
        ("Can I use PayPal as a payment method for Apple services?", "SUBSCRIPTION_BILLING", False, "Regional payment method compatibility guidance.", "SIMPLE", 5),
        ("App Store says 'Verification Required' when trying to download a free app. Why?", "SUBSCRIPTION_BILLING", False, "Explain unpaid previous balance or expired card verification.", "MODERATE", 5),
        ("How to redeem an Apple Gift Card code received for my birthday?", "SUBSCRIPTION_BILLING", False, "App Store profile > Redeem Gift Card guide.", "SIMPLE", 5),
        ("Why was I charged $1 authorization hold on my card by Apple?", "SUBSCRIPTION_BILLING", False, "Explain temporary bank authorization hold for card verification.", "SIMPLE", 5),
        ("How to stop Apple from sending email receipts for every $0.99 transaction?", "SUBSCRIPTION_BILLING", False, "Explain mandatory financial receipt policy.", "SIMPLE", 4),
        ("Can I get student discount on Apple Music? How do I verify my college email?", "SUBSCRIPTION_BILLING", False, "UNiDAYS verification link and guide.", "SIMPLE", 5),
        ("If I cancel Apple TV+ halfway through the month, do I lose access right away?", "SUBSCRIPTION_BILLING", False, "Clarify expiration date policy vs free trial instant termination.", "SIMPLE", 5),
        ("My bank blocked Apple payment because of international transaction fees.", "SUBSCRIPTION_BILLING", False, "Advisory to authorize international e-mandate with issuing bank.", "MODERATE", 4),
        ("How do I request a refund for a duplicated in-app coin purchase in Clash of Clans?", "SUBSCRIPTION_BILLING", False, "reportaproblem.apple.com duplicate purchase reason guide.", "SIMPLE", 5),
        ("Is iCloud private relay included in the $0.99 storage plan?", "SUBSCRIPTION_BILLING", False, "Feature tier entitlement confirmation.", "SIMPLE", 5),
        ("How to remove an expired card from Apple Wallet that won't delete?", "SUBSCRIPTION_BILLING", False, "Wallet card removal steps.", "SIMPLE", 4),

        # Escalate (13)
        ("Apple just deducted $349 from my account without authorization! This is fraud! Return it immediately or I report to police!", "SUBSCRIPTION_BILLING", True, "High-value unauthorized fraudulent deduction requiring immediate financial investigation.", "HOSTILE_EMERGENCY", 5),
        ("I submitted a refund request on reportaproblem.apple.com for a broken $80 app and it was auto-denied! I want a supervisor!", "SUBSCRIPTION_BILLING", True, "Refund appeal after automated rejection; requires senior human discretion.", "HOSTILE_EMERGENCY", 5),
        ("My bank initiated a chargeback for an unrecognized charge, and Apple banned my entire 10-year Apple ID!", "SUBSCRIPTION_BILLING", True, "Chargeback account termination dispute requiring financial risk team resolution.", "HOSTILE_EMERGENCY", 5),
        ("Billed 4 times for the exact same annual $99 Final Cut Pro subscription on the same day.", "SUBSCRIPTION_BILLING", True, "Multiple duplicate annual billing glitch requiring ledger reconciliation.", "MODERATE", 5),
        ("Apple Pay charged my card twice at the grocery store but store receipt says transaction declined.", "SUBSCRIPTION_BILLING", True, "Tokenized merchant transaction dispute requiring bank settlement trace.", "MODERATE", 4),
        ("I cancel this fitness app subscription every month for 6 months and Apple still charges me $29.99! Stop stealing my money!", "SUBSCRIPTION_BILLING", True, "Recurring unauthorized billing bug with hostile repeat customer.", "HOSTILE_EMERGENCY", 5),
        ("Family member with dementia spent $1,200 on mobile games in 2 days. Need compassionate refund review.", "SUBSCRIPTION_BILLING", True, "Vulnerable adult large-sum purchase dispute requiring senior support review.", "AMBIGUOUS_EDGE_CASE", 5),
        ("Developer removed app from App Store after I bought lifetime license for $150 last week. Apple must refund.", "SUBSCRIPTION_BILLING", True, "Abandoned developer app dispute requiring out-of-policy exception.", "MODERATE", 4),
        ("My business corporate card was charged $800 across 20 small microtransactions overnight.", "SUBSCRIPTION_BILLING", True, "Card compromise / high volume fraudulent microtransaction attack.", "HOSTILE_EMERGENCY", 5),
        ("Apple Gift Card showed $100 balance at purchase, but when scratched code was already redeemed. Store refuses help.", "SUBSCRIPTION_BILLING", True, "Tampered retail gift card fraud requiring proof of purchase audit.", "MODERATE", 4),
        ("I was told by phone support I would get a refund in 48 hours, it has been 3 weeks. Ticket #99281.", "SUBSCRIPTION_BILLING", True, "Broken SLA commitment with existing support case ticket.", "MODERATE", 4),
        ("Bank says Apple has put a $500 security pre-auth freeze on my debit card that hasn't cleared in 14 days.", "SUBSCRIPTION_BILLING", True, "Prolonged merchant authorization hold requiring billing team merchant release.", "MODERATE", 4),
        ("Court order requires itemized purchase history of deceased spouse's account for estate settlement.", "SUBSCRIPTION_BILLING", True, "Legal request for financial records requiring Apple Legal handling.", "AMBIGUOUS_EDGE_CASE", 5)
    ]

    # Stratum 6: Connectivity & Accessories (30)
    connectivity_cases = [
        # Auto-handle (23)
        ("AirPods won't connect to my Mac automatically when I open the lid.", "CONNECTIVITY_ACCESSORIES", False, "Bluetooth settings toggle and iCloud automatic switching troubleshooting.", "SIMPLE", 5),
        ("Home Wi-Fi says 'Weak Security' under the network name on iOS 17.", "CONNECTIVITY_ACCESSORIES", False, "Router WPA3/WPA2-AES security configuration advisory.", "SIMPLE", 5),
        ("Bluetooth audio stutters when phone is in my back pocket.", "CONNECTIVITY_ACCESSORIES", False, "RF body attenuation explanation and interference troubleshooting.", "SIMPLE", 4),
        ("How do I unpair an old Apple Watch that I no longer have?", "CONNECTIVITY_ACCESSORIES", False, "Remove device from iCloud.com/find guidance.", "SIMPLE", 5),
        ("Personal Hotspot doesn't show up on my iPad when trying to connect to iPhone.", "CONNECTIVITY_ACCESSORIES", False, "Maximize Compatibility toggle and Instant Hotspot troubleshooting.", "SIMPLE", 5),
        ("AirTag says 'Signal Too Weak' even when standing 10 feet away.", "CONNECTIVITY_ACCESSORIES", False, "Replace CR2032 battery and reset AirTag steps.", "SIMPLE", 5),
        ("How to connect PS5 DualSense controller to iPad via Bluetooth?", "CONNECTIVITY_ACCESSORIES", False, "Controller pairing mode button combination instructions.", "SIMPLE", 5),
        ("iPhone keeps disconnecting from home 5GHz Wi-Fi and falling back to LTE.", "CONNECTIVITY_ACCESSORIES", False, "Reset Network Settings and disable Wi-Fi Assist guidance.", "MODERATE", 5),
        ("Apple Pencil 2nd gen stopped charging when attached to side of iPad.", "CONNECTIVITY_ACCESSORIES", False, "Clean magnetic connector, restart iPad, re-pair pencil.", "SIMPLE", 5),
        ("Can't hear caller unless I switch phone call to speakerphone.", "CONNECTIVITY_ACCESSORIES", False, "Check receiver mesh for dirt and check Hearing Aids routing.", "MODERATE", 4),
        ("How do I turn on 5G Standalone on iPhone 14?", "CONNECTIVITY_ACCESSORIES", False, "Settings > Cellular > Voice & Data options guide.", "SIMPLE", 5),
        ("MagSafe wallet animation doesn't play when snapping onto iPhone 15.", "CONNECTIVITY_ACCESSORIES", False, "NFC read verification and Find My MagSafe wallet setup.", "SIMPLE", 4),
        ("Apple TV remote app on iPhone cannot find Apple TV on same network.", "CONNECTIVITY_ACCESSORIES", False, "Local Network privacy permissions check in Settings.", "SIMPLE", 5),
        ("AirPods volume is super low even at 100% volume slider.", "CONNECTIVITY_ACCESSORIES", False, "Headphone Safety limit check and ear wax mesh cleaning tips.", "SIMPLE", 5),
        ("CarPlay only works wirelessly, won't connect via USB-C cable.", "CONNECTIVITY_ACCESSORIES", False, "USB accessories lock toggle in Face ID settings.", "MODERATE", 5),
        ("Cannot transfer eSIM from old Android phone to new iPhone automatically.", "CONNECTIVITY_ACCESSORIES", False, "Explain cross-platform eSIM transfer limitation; direct to carrier.", "MODERATE", 4),
        ("Smart Keyboard Folio typing double letters on iPad Air.", "CONNECTIVITY_ACCESSORIES", False, "Clean Smart Connector magnetic pins with microfiber cloth.", "SIMPLE", 4),
        ("Apple Watch battery drain when connected to Bluetooth headphones during run.", "CONNECTIVITY_ACCESSORIES", False, "Explain standalone GPS + BT streaming power consumption.", "SIMPLE", 4),
        ("AirDrop fails with 'Declined' immediately when sending 50 photos to friend.", "CONNECTIVITY_ACCESSORIES", False, "AirDrop contacts only vs everyone 10 mins setting, transfer in smaller batches.", "SIMPLE", 5),
        ("iPhone keeps connecting to neighbor's open Wi-Fi instead of home network.", "CONNECTIVITY_ACCESSORIES", False, "Turn off Auto-Join on public Wi-Fi networks.", "SIMPLE", 5),
        ("Do AirPods Pro 2 USB-C work with non-Apple Android devices?", "CONNECTIVITY_ACCESSORIES", False, "Confirm standard Bluetooth audio compatibility and feature limitations.", "SIMPLE", 5),
        ("How to rename Bluetooth devices like car audio in iPhone settings?", "CONNECTIVITY_ACCESSORIES", False, "Bluetooth device info (i) icon rename instructions.", "SIMPLE", 5),
        ("Why does cellular say 'SOS only' at the airport?", "CONNECTIVITY_ACCESSORIES", False, "Explain no carrier coverage / roaming data toggle.", "SIMPLE", 5),

        # Escalate (7)
        ("Wi-Fi and Bluetooth toggles are completely greyed out and cannot be turned on at all. Network reset failed.", "CONNECTIVITY_ACCESSORIES", True, "Hardware failure of onboard Wi-Fi/BT baseband IC requiring board-level repair.", "MODERATE", 5),
        ("Apple Watch caught fire on my wrist while charging on the official magnetic puck!", "CONNECTIVITY_ACCESSORIES", True, "Severe thermal incident / bodily harm risk requiring immediate safety escalation.", "HOSTILE_EMERGENCY", 5),
        ("My iPhone 14 completely lost IMEI number and modem firmware is blank in About settings. Zero cellular.", "CONNECTIVITY_ACCESSORIES", True, "Catastrophic baseband modem hardware failure; device cannot register on any network.", "MODERATE", 5),
        ("AirPods exploded with a loud pop in my ear while listening to music. Left ear is ringing painfully.", "CONNECTIVITY_ACCESSORIES", True, "Critical acoustic/battery injury incident requiring urgent legal/executive support.", "HOSTILE_EMERGENCY", 5),
        ("CarPlay keeps locking up vehicle's digital gauge cluster speedometer while driving on highway.", "CONNECTIVITY_ACCESSORIES", True, "Automotive safety defect report requiring Tier-3 engineering investigation.", "HOSTILE_EMERGENCY", 4),
        ("Brand new $250 AirPods Pro arrived with an empty box from Apple online store!", "CONNECTIVITY_ACCESSORIES", True, "Stolen package in transit / logistics claim requiring carrier loss report.", "MODERATE", 5),
        ("iPad Smart Connector port is sparking when attaching official Magic Keyboard.", "CONNECTIVITY_ACCESSORIES", True, "Electrical short on exterior hardware contact pins.", "MODERATE", 5)
    ]

    all_cases = battery_cases + os_cases + security_cases + damage_cases + billing_cases + connectivity_cases
    assert len(all_cases) == 200, f"Expected 200 cases, got {len(all_cases)}"

    for idx, (tweet, intent, escalate, reason, stratum, human_score) in enumerate(all_cases, 1):
        case_id = f"GOLD-{idx:03d}"
        samples.append({
            "id": case_id,
            "tweet_text": tweet,
            "ground_truth_intent": intent,
            "ground_truth_escalate": escalate,
            "escalation_reason": reason,
            "complexity_stratum": stratum,
            "human_quality_score": human_score
        })

    return samples

def main():
    os.makedirs(r"C:\Users\mukil\hiver-support-agent\data", exist_ok=True)
    
    # 1. Write KB
    kb_path = r"C:\Users\mukil\hiver-support-agent\data\apple_support_kb.jsonl"
    with open(kb_path, "w", encoding="utf-8") as f:
        for item in KB_ITEMS:
            f.write(json.dumps(item) + "\n")
    print(f"Generated KB with {len(KB_ITEMS)} historical grounded items at {kb_path}")

    # 2. Write Golden 200 Set
    golden_samples = generate_golden_dataset()
    golden_path = r"C:\Users\mukil\hiver-support-agent\data\golden_eval_set_200.jsonl"
    with open(golden_path, "w", encoding="utf-8") as f:
        for item in golden_samples:
            f.write(json.dumps(item) + "\n")
    print(f"Generated Golden Evaluation Set with {len(golden_samples)} samples at {golden_path}")

    # Verify distribution
    intent_counts = {}
    escalate_counts = {True: 0, False: 0}
    strata_counts = {}
    for s in golden_samples:
        intent_counts[s["ground_truth_intent"]] = intent_counts.get(s["ground_truth_intent"], 0) + 1
        escalate_counts[s["ground_truth_escalate"]] += 1
        strata_counts[s["complexity_stratum"]] = strata_counts.get(s["complexity_stratum"], 0) + 1

    print("\nDataset Verification:")
    print("Intent Distribution:", intent_counts)
    print("Escalation Distribution:", escalate_counts)
    print("Stratum Distribution:", strata_counts)

if __name__ == "__main__":
    main()
