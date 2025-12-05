# Flask Pandas Documentation

Welcome to the Flask Pandas documentation. This directory contains comprehensive guides for deploying, testing, and maintaining the Flask Pandas application.

---

## 📚 Quick Navigation

### Getting Started
- **[Main README](../README.md)** - Project overview and quick start guide

### Deployment & Operations
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - 📘 **Comprehensive deployment guide**
  - Environment variables configuration
  - 1Password setup and integration
  - Deployment procedures (local, production, DHI)
  - Rollback procedures
  - Troubleshooting guide

### Testing
- **[TESTING.md](TESTING.md)** - 📗 **Complete testing documentation**
  - Test environment setup
  - Running tests (unit, integration, coverage)
  - Test fixtures and markers
  - CI/CD integration
  - Troubleshooting test issues

### Configuration Guides
- **[LARGE_FILE_UPLOAD_GUIDE.md](LARGE_FILE_UPLOAD_GUIDE.md)** - 📄 Large file handling (10GB+)
  - Configuration for large uploads
  - Memory management
  - Performance optimization
  - Current deployment commands

- **[PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)** - 📄 Legacy production guide
  - Redis configuration
  - Nginx setup
  - Sentry monitoring
  - Gunicorn configuration
  - *Note: See DEPLOYMENT.md for current deployment procedures*

### Project Documentation
- **[WARP.md](WARP.md)** - 🔧 Project-specific AI coding rules
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - 📋 Multi-environment implementation plan
- **[MAKEFILE_VALIDATION.md](MAKEFILE_VALIDATION.md)** - ✅ Makefile testing documentation
- **[PHASE_6_7_VALIDATION_SUMMARY.md](PHASE_6_7_VALIDATION_SUMMARY.md)** - ✅ Validation report

---

## 🚀 Common Tasks

### Deploy Locally
```bash
# From project root
make dev

# Or
./deploy.sh local up
```

### Run Tests
```bash
# From project root
make test

# With coverage
make test-coverage
```

### Deploy to Production
```bash
# Sign in to 1Password
op signin

# Deploy
make prod-up

# View logs
make prod-logs
```

---

## 📖 Documentation Structure

### Core Documentation (Start Here)
1. **[DEPLOYMENT.md](DEPLOYMENT.md)** - If you're deploying or operating the application
2. **[TESTING.md](TESTING.md)** - If you're writing or running tests

### Reference Documentation
- **[LARGE_FILE_UPLOAD_GUIDE.md](LARGE_FILE_UPLOAD_GUIDE.md)** - For large file handling configuration
- **[PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)** - For advanced production features (Redis, Nginx, Sentry)

### Project Management
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - Implementation history and plan
- **[MAKEFILE_VALIDATION.md](MAKEFILE_VALIDATION.md)** - Makefile testing results
- **[PHASE_6_7_VALIDATION_SUMMARY.md](PHASE_6_7_VALIDATION_SUMMARY.md)** - Final validation report
- **[WARP.md](WARP.md)** - AI coding assistant rules

---

## 🎯 Quick Links by Role

### For Developers
1. [TESTING.md](TESTING.md) - How to run and write tests
2. [../README.md](../README.md) - Project overview and setup
3. [DEPLOYMENT.md](DEPLOYMENT.md#local-development-deployment) - Local development deployment

### For DevOps/Operations
1. [DEPLOYMENT.md](DEPLOYMENT.md) - Complete deployment guide
2. [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting) - Troubleshooting section
3. [DEPLOYMENT.md](DEPLOYMENT.md#rollback-procedures) - Rollback procedures

### For System Architects
1. [LARGE_FILE_UPLOAD_GUIDE.md](LARGE_FILE_UPLOAD_GUIDE.md) - Large file architecture
2. [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md) - Production infrastructure
3. [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - System design decisions

---

## 📝 Document Maintenance

### Last Updated
- **DEPLOYMENT.md**: 2025-12-05
- **TESTING.md**: 2025-12-05
- **README.md** (this file): 2025-12-05

### Contributing
When updating documentation:
1. Keep guides focused and concise
2. Update "Last Updated" dates
3. Maintain cross-references between documents
4. Test all code examples and commands
5. Update this index if adding new documents

---

## 🔍 Need Help?

### Can't find what you're looking for?

**Deployment Issues**: See [DEPLOYMENT.md - Troubleshooting](DEPLOYMENT.md#troubleshooting)

**Test Issues**: See [TESTING.md - Troubleshooting](TESTING.md#troubleshooting)

**Configuration Questions**: Check [DEPLOYMENT.md - Environment Variables](DEPLOYMENT.md#environment-variables)

**1Password Setup**: See [DEPLOYMENT.md - 1Password Vault Structure](DEPLOYMENT.md#1password-vault-structure)

---

## 📊 Documentation Statistics

| Document | Lines | Focus Area |
|----------|-------|------------|
| DEPLOYMENT.md | 662 | Deployment & Operations |
| TESTING.md | 681 | Testing & QA |
| LARGE_FILE_UPLOAD_GUIDE.md | ~250 | Performance Configuration |
| PRODUCTION_DEPLOYMENT_GUIDE.md | ~500 | Advanced Production Setup |
| IMPLEMENTATION_PLAN.md | ~800 | Project Planning |

**Total**: ~3,000 lines of comprehensive documentation

---

**Maintained by**: Tom Twyman  
**Project**: Flask Pandas - Workload Parser  
**Repository**: [github.com/fr0gger03/flask_pandas](https://github.com/fr0gger03/flask_pandas)
