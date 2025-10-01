# MouseAlerts Admin Security Guide

This document outlines the security measures implemented for the MouseAlerts admin dashboard and provides setup instructions.

## 🔒 Security Features

### 1. **Database Admin Roles**
- **Admin Model**: Dedicated admin table with roles and permissions
- **Role-Based Access**: `super_admin`, `admin`, `moderator` roles
- **Permission System**: Granular permissions for different admin functions
- **Audit Logging**: All admin actions are logged for security

### 2. **Environment-Based Access Control**
- **Admin Emails**: Configure admin emails via `ADMIN_EMAILS`
- **Admin User IDs**: Configure admin user IDs via `ADMIN_USER_IDS`
- **IP Whitelisting**: Optional IP restrictions via `ADMIN_IP_WHITELIST`
- **Secret Key**: Admin operations protected by `ADMIN_SECRET_KEY`

### 3. **Search Engine Protection**
- **robots.txt**: Blocks admin routes from search engines
- **sitemap.xml**: Excludes admin pages from sitemap
- **Meta Tags**: Admin pages have noindex meta tags

## 🛠️ Setup Instructions

### 1. **Environment Variables**

Create a `.env.local` file with admin configuration:

```bash
# Admin Access Control
ADMIN_EMAILS=admin@mousealerts.com,your-email@domain.com
ADMIN_USER_IDS=admin-user-123,your-user-id-456

# Admin Security
ADMIN_SECRET_KEY=your-super-secret-admin-key-change-this-in-production
ADMIN_IP_WHITELIST=192.168.1.100,10.0.0.50  # Optional

# Admin Session Settings
ADMIN_SESSION_TIMEOUT=60  # minutes
ADMIN_REFRESH_INTERVAL=30  # seconds

# Admin Security Features
ADMIN_2FA_REQUIRED=false  # Set to true in production
ADMIN_AUDIT_LOGGING=true  # Log all admin actions
```

### 2. **Database Setup**

Run the database migration to create admin tables:

```bash
# Create admin tables
alembic revision --autogenerate -m "Add admin tables"
alembic upgrade head
```

### 3. **Create Admin User**

Use the admin service to create your first admin user:

```python
from api.services.admin_service import AdminService
from db import get_db

# Create admin access for your user
db = next(get_db())
admin_service = AdminService(db)

# Create super admin
admin_service.create_admin(
    user_id="your-user-id",
    role="super_admin",
    permissions={
        "user_management": True,
        "system_monitoring": True,
        "billing_access": True,
        "admin_management": True
    }
)
```

## 🔐 Security Best Practices

### 1. **Production Security**
- **Change Secret Key**: Use a strong, random `ADMIN_SECRET_KEY`
- **IP Whitelisting**: Restrict admin access to your office/home IPs
- **Enable 2FA**: Set `ADMIN_2FA_REQUIRED=true` in production
- **Audit Logging**: Keep `ADMIN_AUDIT_LOGGING=true` for security monitoring
- **Regular Rotation**: Rotate `ADMIN_SECRET_KEY` regularly

### 2. **Access Control**
- **Principle of Least Privilege**: Give admins only the permissions they need
- **Regular Audits**: Review admin access and permissions regularly
- **Session Management**: Monitor admin session timeouts
- **IP Monitoring**: Log and monitor admin access IPs

### 3. **Monitoring**
- **Admin Actions**: All admin actions are logged with timestamps
- **Failed Access**: Failed admin access attempts are logged
- **IP Tracking**: Admin access IPs are recorded
- **Permission Changes**: Admin permission changes are audited

## 📊 Admin Roles & Permissions

### **Super Admin**
- Full system access
- Can manage other admins
- Can modify admin permissions
- Access to all admin features

### **Admin**
- User management
- System monitoring
- Billing access
- Cannot manage other admins

### **Moderator**
- User support access
- Basic system monitoring
- Limited admin features

## 🚫 What's Blocked from Search Engines

### **robots.txt Exclusions**
```
Disallow: /admin
Disallow: /admin/
Disallow: /admin/*
Disallow: /api/admin
Disallow: /api/admin/
```

### **sitemap.xml Exclusions**
- Admin routes are not included in sitemap
- Only public pages are indexed

## 🔍 Security Monitoring

### **Admin Access Logs**
- User ID and email
- Access timestamp
- IP address
- User agent
- Action performed

### **Failed Access Attempts**
- Non-admin users attempting admin access
- IP addresses not in whitelist
- Invalid admin credentials

### **Permission Changes**
- Admin role modifications
- Permission updates
- Admin deactivation

## 🚨 Security Alerts

The system will log security events:

1. **Unauthorized Access**: Non-admin users accessing admin routes
2. **IP Violations**: Admin access from non-whitelisted IPs
3. **Permission Changes**: Admin permission modifications
4. **Admin Creation**: New admin accounts created
5. **Admin Deactivation**: Admin accounts deactivated

## 📝 API Security

### **Admin Endpoints**
- All admin endpoints require authentication
- Permission-based access control
- IP whitelisting (if configured)
- Audit logging for all actions

### **Middleware Protection**
- `require_admin_access`: Basic admin access
- `require_user_management`: User management permission
- `require_system_monitoring`: System monitoring permission
- `require_billing_access`: Billing access permission
- `require_super_admin`: Super admin access

## 🔧 Troubleshooting

### **Common Issues**

1. **Access Denied**: Check if user is in admin list
2. **IP Blocked**: Verify IP is in whitelist (if configured)
3. **Permission Denied**: Check user's admin permissions
4. **Session Timeout**: Check session timeout settings

### **Debug Commands**

```python
# Check if user is admin
admin_service.is_admin(user_id)

# Check admin permissions
admin_service.has_permission(user_id, "user_management")

# Get admin info
admin_service.get_admin_info(user_id)
```

## 📞 Support

For admin security issues:
1. Check admin logs for access attempts
2. Verify environment variables are set correctly
3. Ensure database admin tables are created
4. Check IP whitelist configuration

## 🔄 Updates

To update admin security:
1. Update environment variables
2. Restart the application
3. Test admin access
4. Monitor access logs
