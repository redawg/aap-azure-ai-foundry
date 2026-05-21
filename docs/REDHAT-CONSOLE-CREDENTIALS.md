# Red Hat console credentials for AAP 2.6

Two different console.redhat.com flows apply to your workshop cluster. Do not mix them up.

## 1. Service account (article [7112649](https://access.redhat.com/articles/7112649))

**Use for:** Automation Analytics and subscription attach — **not** for syncing collections from Automation Hub.

Red Hat states in that article:

> Service account authentication does not affect or change the process for authenticating to automation hub required for syncing content.

### Steps (Hybrid Cloud Console)

1. Open [console.redhat.com → IAM → Service accounts](https://console.redhat.com/iam/service-accounts).
2. **Create service account** — save **client ID** and **client secret** (shown once).
3. **User Access → Groups** — add the service account to:
   - **Automation analytics viewer** (for Analytics data in console)
   - **Subscriptions viewer** (optional, to attach subscription via service account tab)
4. In AAP UI: **Settings → Automation Execution → System → Edit**
   - **Red Hat client ID for Analytics** = client ID
   - **Red Hat client secret for Analytics** = client secret
   - Enable **Gather data for Automation Analytics**
5. Run a job; confirm data under [Automation Analytics](https://console.redhat.com/ansible/automation-analytics/reports).

### Ansible (after you have the secrets)

```bash
ansible-playbook playbooks/aap-redhat-analytics-service-account.yml \
  -e redhat_analytics_client_id='…' \
  -e redhat_analytics_client_secret='…' \
  --ask-vault-pass   # if stored in vault
```

---

## 2. Automation Hub / Galaxy API token (collections sync)

**Use for:** Credential type **Ansible Galaxy/Automation Hub API Token** (Controller credential type id `19`).

Workshop cluster already has managed credential **Ansible Galaxy** (id `2`) pointing at `https://galaxy.ansible.com/` with **no API token**. For certified content from Red Hat Hub, point it at console Automation Hub and add a token.

### Steps (get token from console)

1. Log in to [console.redhat.com](https://console.redhat.com).
2. Open **Automation Hub** → [Get API token](https://console.redhat.com/ansible/automation-hub/token)  
   (or navigate: **Red Hat Ansible Automation Platform → Automation Hub → Connect to Hub → Token**).
3. Click **Load token** (or equivalent). Copy:
   - **API token** (long offline token)
   - **Server URL** (e.g. `https://console.redhat.com/api/automation-hub/`)
   - **Auth server URL** (SSO token endpoint, if shown)
4. In AAP UI: **Automation Execution → Credentials → Ansible Galaxy → Edit**
   - **Galaxy Server URL** = Server URL from step 3
   - **Auth Server URL** = Auth URL from step 3 (if required)
   - **API Token** = token from step 3
5. **Automation Execution → Organizations → Default → Galaxy Credentials** — ensure this credential is selected.
6. Sync a project or run `ansible-galaxy collection install …` from a job using that org.

### Ansible (after you have the token)

```bash
ansible-playbook playbooks/aap-redhat-galaxy-credential.yml \
  -e aap_galaxy_hub_url='https://console.redhat.com/api/automation-hub/' \
  -e aap_galaxy_auth_url='https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token' \
  -e aap_galaxy_api_token='…' \
  -e aap_galaxy_credential_name='Ansible Galaxy'
```

Do not commit tokens; use `ansible-vault` or export vars only in your shell.

---

## Quick reference (workshop)

| Goal | Console URL | AAP where to paste |
|------|-------------|-------------------|
| Analytics (7112649) | [Service accounts](https://console.redhat.com/iam/service-accounts) | Settings → Automation Execution → System |
| Hub collections | [Automation Hub token](https://console.redhat.com/ansible/automation-hub/token) | Credentials → Ansible Galaxy |
| Subscription (7112649) | Same service account + Subscriptions viewer group | Settings → Subscription → Service Account tab |
