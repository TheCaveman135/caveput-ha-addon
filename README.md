# CavePut Add-ons for Home Assistant

Custom Home Assistant add-on repository for CavePut label printing.

## Add to Home Assistant

1. Go to **Settings → Add-ons → Add-on Store**
2. Click the three-dot menu → **Repositories**
3. Add: `https://github.com/TheCaveman135/caveput-ha-addon`
4. Find **CavePut DB** in the store and install it

## Add-ons

### CavePut DB

A local ingredient database that syncs from Zenput every Sunday night.
The CavePut iOS app connects to this instead of Zenput directly.

**Features:**
- Syncs ingredients, phases, and label templates from Zenput
- Stores everything locally — app works offline
- JWT-authenticated REST API
- Manual sync trigger from within Home Assistant
- Configurable sync schedule
