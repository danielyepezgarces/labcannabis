# User Creation Form Changes - Summary

## Changes Made (Commit: ce1725f)

### 1. Removed `usable_password` Field

**Before:**
```
User Creation Fields:
- username
- usable_password  ← REMOVED
- password1
- password2
```

**After:**
```
User Creation Fields:
- username
- password1
- password2
```

The `usable_password` field has been removed from the user creation form. This field was showing the Spanish text:
> "Determina si el usuario podrá autenticarse usando una contraseña. Si está deshabilitado, el usuario aún podría autenticarse mediante otros métodos, como Single Sign-On o LDAP."

Now users are created with password authentication by default, which is the standard behavior.

### 2. Solicitante Role Assigned by Default

New users are automatically assigned to the **Solicitante** group when created through the admin panel.

**Implementation:**
```python
def save_model(self, request, obj, form, change):
    """Save user and assign Solicitante group by default for new users"""
    super().save_model(request, obj, form, change)
    
    # If this is a new user (not editing existing), add to Solicitante group
    if not change:
        try:
            solicitante_group = Group.objects.get(name='Solicitante')
            obj.groups.add(solicitante_group)
        except Group.DoesNotExist:
            # Group doesn't exist yet, skip
            pass
```

### 3. Test Coverage

Added 4 new tests to verify the behavior:

1. ✅ `test_add_fieldsets_no_usable_password` - Verifies usable_password is not in the form
2. ✅ `test_add_fieldsets_has_required_fields` - Verifies required fields are present
3. ✅ `test_new_user_gets_solicitante_group` - Verifies new users get Solicitante role
4. ✅ `test_editing_user_doesnt_add_group_again` - Verifies editing doesn't duplicate groups

**All 18 tests passing** (14 original + 4 new)

## User Experience

### Creating a New User (Admin Panel)

1. Navigate to: **Admin → Authentication and Authorization → Users**
2. Click **"Add User"**
3. Fill in:
   - Username
   - Password
   - Password confirmation
4. Click **Save**
5. User is created with:
   - ✅ Password authentication enabled (no usable_password checkbox)
   - ✅ Automatically assigned to **Solicitante** group

### Benefits

1. **Simpler form** - Removed confusing usable_password field
2. **Default role** - New users automatically have Solicitante permissions
3. **Standard authentication** - Password authentication is the default method
4. **Consistent behavior** - All new users start with the same baseline permissions

## Technical Details

### Files Modified

- `solicitudes/admin.py` - Added custom UserAdmin configuration
- `solicitudes/tests.py` - Added 4 unit tests

### Code Changes

```python
@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """Custom User admin with Unfold styling and Solicitante default role"""
    
    # Override add_fieldsets to remove usable_password field
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Save user and assign Solicitante group by default for new users"""
        super().save_model(request, obj, form, change)
        
        if not change:  # New user
            try:
                solicitante_group = Group.objects.get(name='Solicitante')
                obj.groups.add(solicitante_group)
            except Group.DoesNotExist:
                pass
```

## Verification

Run the test suite to verify:
```bash
python manage.py test solicitudes.tests.UserAdminTest
```

Expected output:
```
test_add_fieldsets_has_required_fields ... ok
test_add_fieldsets_no_usable_password ... ok
test_editing_user_doesnt_add_group_again ... ok
test_new_user_gets_solicitante_group ... ok

----------------------------------------------------------------------
Ran 4 tests in X.XXXs

OK
```

## Summary

✅ Removed confusing `usable_password` field from user creation form
✅ New users automatically get Solicitante role
✅ Password authentication is now the default
✅ All tests passing (18/18)
✅ Changes committed in ce1725f
