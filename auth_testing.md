# Auth Testing Playbook (SecureCBT)

Step 1: MongoDB
```
mongosh
use test_database
db.admins.find({role:"admin"}).pretty()
```
Verify bcrypt hash starts with `$2b$`.

Step 2: API
```
curl -X POST http://localhost:8001/api/auth/login -H "Content-Type: application/json" -d '{"email":"admin@axelbit.com","password":"ax3lb1t"}'
# → {access_token, user}
curl http://localhost:8001/api/auth/me -H "Authorization: Bearer <token>"
```
Brute force: 5 failed logins per ip:email → 15 min lockout.
