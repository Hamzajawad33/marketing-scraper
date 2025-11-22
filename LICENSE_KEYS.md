# 🔑 Nebula Crest License Keys

## License Key Authentication System

The application now uses a **license key authentication system** instead of login/signup. Simply enter a valid license key to activate and access the tool.

---

## Valid License Keys

### 🔧 Developer License (1 Key)

**Full Access - Unlimited Usage - Priority Support**

```
DEV1-2024-NBLC-FULL-A7X9
```

**Features:**
- ✅ Unlimited searches
- ✅ Advanced features enabled
- ✅ Priority support
- ✅ No restrictions

---

### 👥 Client Licenses (10 Keys)

**Standard Access - 1000 Results Limit per Search**

```
CLT1-2024-NBLC-STD1-K4M2
CLT2-2024-NBLC-STD2-P9W5
CLT3-2024-NBLC-STD3-R3Y8
CLT4-2024-NBLC-STD4-T6L1
CLT5-2024-NBLC-STD5-V2N7
CLT6-2024-NBLC-STD6-X8Q4
CLT7-2024-NBLC-STD7-Z1H9
CLT8-2024-NBLC-STD8-B5J3
CLT9-2024-NBLC-STD9-D9F6
CL10-2024-NBLC-ST10-G3K8
```

**Features:**
- ✅ Up to 1000 results per search
- ✅ Advanced features enabled
- ⚠️ Standard support
- ⚠️ Some limitations may apply

---

## How to Use

1. **Start the application** by running `python app.py`
2. **Browser will open** to the license activation page
3. **Enter a license key** from the list above
4. **Click "Activate License"**
5. **Access granted!** You'll be redirected to the scraper tool

---

## License Key Format

All license keys follow this format:
```
XXXX-XXXX-XXXX-XXXX-XXXX
```

- **Part 1:** License type identifier (DEV1, CLT1-10, CL10)
- **Part 2:** Year (2024)
- **Part 3:** Product code (NBLC = Nebula Crest)
- **Part 4:** License tier (FULL/STD1-10/ST10)
- **Part 5:** Unique validation code

---

## Session Management

- License keys are stored in your browser session
- Your session persists until you click "Logout"
- Reactivation required after logout or browser restart
- Multiple users can use the same key (shared licenses)

---

## Technical Details

### Database Tracking
All license activations are tracked in `nebula_users.db`:
- License key
- License type (developer/client)
- Activation timestamp
- Last used timestamp

### Security Features
- Keys validated server-side
- Session-based authentication
- Automatic format validation
- Case-insensitive input

---

## Quick Test

**Try the Developer Key:**
```
DEV1-2024-NBLC-FULL-A7X9
```

This will give you full unlimited access to test all features!

---

## License Deactivation

To deactivate/switch license:
1. Click the **Logout** button in the app
2. You'll be returned to the license page
3. Enter a different license key if needed

---

> **Note:** All keys are pre-generated and hardcoded in `auth.py`. No database authentication required - simply match against the valid key list!
