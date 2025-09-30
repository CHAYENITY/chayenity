# 🗂️ FILE CONSOLIDATION PLAN

## ✅ **ANSWER: Use Single File (`security.py`)**

**You can DELETE `enhanced_security.py` - everything important is now in `security.py`**

## 📋 **What We've Done:**

### **✅ Enhanced `security.py` with:**
- 🔑 **Token creation with JTI** (`create_access_token_with_jti`, `create_refresh_token_with_jti`)
- 🔒 **Rate limiting** for refresh endpoints
- 📝 **Database model templates** (to add to `models.py`)
- ⚡ **Backward compatibility** (old functions still work)

### **🗑️ Can Delete:**
- `enhanced_security.py` - No longer needed

## 🚀 **Next Steps:**

### **1. Update your auth route to use enhanced functions:**
```python
# In auth_route.py, replace:
access_token = create_access_token(data={"sub": str(user.id)})
refresh_token = create_refresh_token(data={"sub": str(user.id)})

# With:
access_token, access_jti = create_access_token_with_jti(data={"sub": str(user.id)})
refresh_token, refresh_jti = create_refresh_token_with_jti(data={"sub": str(user.id)})
```

### **2. Add security models to `models.py`:**
```python
# Copy the UserSession and BlacklistedToken models from the comments in security.py
```

### **3. Run database migration:**
```bash
# Create new migration for the security tables
python scripts/init_db_directly.py  # Or use Alembic if fixed
```

## 🎯 **Benefits of Single File Approach:**
- ✅ **No duplication** of functions
- ✅ **Easier maintenance** 
- ✅ **Clear organization**
- ✅ **Gradual migration** (old functions still work)
- ✅ **Enhanced security** available when needed

## 🔧 **File Status:**
- **Keep**: `security.py` ⭐ (Enhanced)
- **Delete**: `enhanced_security.py` ❌ (No longer needed)

---

**Result: Single, powerful security file with both basic and advanced features! 🛡️**