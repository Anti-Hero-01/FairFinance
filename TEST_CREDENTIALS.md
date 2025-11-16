# FairFinance - Test User Credentials

All test users have been created in the database. Use these credentials to login and test different roles.

## 🔐 USER ROLE (5 accounts)

Regular users can:
- Apply for loans
- View their applications
- See SHAP explanations
- Use voice assistant
- Manage consent
- View profile explanations

| # | Email | Password | Name |
|---|-------|----------|------|
| 1 | `user1@fairfinance.com` | `user123` | John Doe |
| 2 | `user2@fairfinance.com` | `user123` | Jane Smith |
| 3 | `user3@fairfinance.com` | `user123` | Bob Johnson |
| 4 | `user4@fairfinance.com` | `user123` | Alice Williams |
| 5 | `user5@fairfinance.com` | `user123` | Charlie Brown |

---

## 👑 ADMIN ROLE (5 accounts)

Admin users can:
- All user features PLUS:
- Access Governance Dashboard
- View fairness reports
- Override loan decisions
- View audit trails
- Access all decision logs

| # | Email | Password | Name |
|---|-------|----------|------|
| 1 | `admin1@fairfinance.com` | `admin123` | Admin One |
| 2 | `admin2@fairfinance.com` | `admin123` | Admin Two |
| 3 | `admin3@fairfinance.com` | `admin123` | Admin Three |
| 4 | `admin4@fairfinance.com` | `admin123` | Admin Four |
| 5 | `admin5@fairfinance.com` | `admin123` | Admin Five |

---

## 🔍 AUDITOR ROLE (5 accounts)

Auditor users can:
- All user features PLUS:
- Access Governance Dashboard
- View fairness reports
- View audit trails
- Access all decision logs
- **Cannot** override decisions (admin only)

| # | Email | Password | Name |
|---|-------|----------|------|
| 1 | `auditor1@fairfinance.com` | `auditor123` | Auditor One |
| 2 | `auditor2@fairfinance.com` | `auditor123` | Auditor Two |
| 3 | `auditor3@fairfinance.com` | `auditor123` | Auditor Three |
| 4 | `auditor4@fairfinance.com` | `auditor123` | Auditor Four |
| 5 | `auditor5@fairfinance.com` | `auditor123` | Auditor Five |

---

## 🚀 Quick Login Guide

1. **Open Frontend**: http://localhost:3000
2. **Click "Sign in"** or navigate to login page
3. **Enter any email and password** from the tables above
4. **Click "Sign in"**

### Recommended Test Flow

1. **Start with USER role** (`user1@fairfinance.com` / `user123`)
   - Apply for a loan
   - View explanations
   - Test voice assistant
   - Manage consent

2. **Then try ADMIN role** (`admin1@fairfinance.com` / `admin123`)
   - Access Governance Dashboard
   - View fairness metrics
   - Test admin override feature

3. **Finally try AUDITOR role** (`auditor1@fairfinance.com` / `auditor123`)
   - View audit trails
   - Check decision logs
   - Review fairness reports

---

## 📝 Notes

- All passwords are simple for testing: `user123`, `admin123`, `auditor123`
- All accounts are active and ready to use
- You can create more users via the registration page
- To recreate test users, run: `python backend/create_test_users.py`

---

**Happy Testing! 🎉**

