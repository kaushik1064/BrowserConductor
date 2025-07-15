# Improved Local Automation Instructions

## Current Status
Your stealth automation is working well - it successfully bypassed the access restrictions and loaded the Ajio.com page! The only issue now is finding the correct login button selector.

## Next Steps to Fix Login Button Detection

### Option 1: Run Debug Script (Recommended)
```bash
python quick_debug.py
```
This will:
1. Open Ajio.com in a visible browser
2. Check for access restrictions
3. Look for login-related elements
4. Help you manually identify the login button

### Option 2: Manual Inspection
1. Open Ajio.com in your regular browser
2. Right-click on the "Sign In" or "Login" button
3. Select "Inspect Element"
4. Note the HTML structure and text

### Option 3: Try Updated Stealth Agent
The updated stealth agent now has 25+ different selectors and should be much more likely to find the login button. Try running:

```bash
python run_stealth.py
```

## Common Ajio.com Login Button Patterns

Based on typical e-commerce sites, the login button might be:

1. **Text-based**: 
   - "Sign In"
   - "Login" 
   - "Account"

2. **Location**:
   - Top right corner of header
   - In navigation menu
   - Mobile hamburger menu

3. **HTML structure**:
   ```html
   <button>Sign In</button>
   <a href="/login">Login</a>
   <span onclick="...">Account</span>
   ```

## If Login Button Still Not Found

### Update the selector manually:
Edit `agents/stealth_login_agent.py` and add the correct selector to the `login_selectors` list:

```python
login_selectors = [
    # Add your discovered selector here
    'your-discovered-selector-here',
    
    # Existing selectors...
    'button:has-text("Sign In")',
    # ... rest of selectors
]
```

### Common fixes:
1. **Case sensitivity**: Try "SIGN IN" vs "Sign In"
2. **Spacing**: Try "SignIn" vs "Sign In" 
3. **Different text**: Try "Account", "My Account", "Login"
4. **Icon buttons**: Look for user icons or account icons

## Alternative Approach: Direct URL
If the login button is still elusive, try navigating directly to the login page:

```python
# In stealth_login_agent.py, modify navigate_to_ajio method:
await self.page.goto('https://www.ajio.com/login', wait_until='domcontentloaded')
```

## Success Indicators
You'll know it's working when you see:
```
🔐 Looking for login button...
🔍 Trying selector 1: button:has-text("Sign In")
✅ Found clickable login element: 'Sign In' with selector: button:has-text("Sign In")
✅ Login button clicked successfully
```

## Troubleshooting Tips

1. **Try headed mode first**: `headless=False` to see what's happening
2. **Check page load**: Make sure the page fully loads before looking for elements
3. **Network timing**: Add longer waits if page loads slowly
4. **Mobile vs Desktop**: Ajio might show different layouts

The stealth system is working perfectly - we just need to find the right button!