"""
Master list of 100 apps to research, organized by category.
"""

APPS = [
    # CRM & Sales (10)
    {"name": "Salesforce", "category": "CRM & Sales", "hint_url": "https://developer.salesforce.com/docs"},
    {"name": "HubSpot", "category": "CRM & Sales", "hint_url": "https://developers.hubspot.com/docs"},
    {"name": "Pipedrive", "category": "CRM & Sales", "hint_url": "https://developers.pipedrive.com/docs/api/v1"},
    {"name": "Attio", "category": "CRM & Sales", "hint_url": "https://developers.attio.com/docs"},
    {"name": "Twenty", "category": "CRM & Sales", "hint_url": "https://twenty.com/developers"},
    {"name": "Podio", "category": "CRM & Sales", "hint_url": "https://developers.podio.com"},
    {"name": "Zoho CRM", "category": "CRM & Sales", "hint_url": "https://www.zoho.com/crm/developer/docs/api/v6/"},
    {"name": "Close", "category": "CRM & Sales", "hint_url": "https://developer.close.com"},
    {"name": "Copper", "category": "CRM & Sales", "hint_url": "https://developer.copper.com"},
    {"name": "DealCloud", "category": "CRM & Sales", "hint_url": "https://dealcloud.com/resources/integrations/"},

    # Support (10)
    {"name": "Zendesk", "category": "Support", "hint_url": "https://developer.zendesk.com/api-reference"},
    {"name": "Intercom", "category": "Support", "hint_url": "https://developers.intercom.com/docs"},
    {"name": "Freshdesk", "category": "Support", "hint_url": "https://developers.freshdesk.com/api"},
    {"name": "Front", "category": "Support", "hint_url": "https://dev.frontapp.com/docs"},
    {"name": "Pylon", "category": "Support", "hint_url": "https://docs.usepylon.com"},
    {"name": "LiveAgent", "category": "Support", "hint_url": "https://www.liveagent.com/app/api/"},
    {"name": "Plain", "category": "Support", "hint_url": "https://plain.com/docs"},
    {"name": "Help Scout", "category": "Support", "hint_url": "https://developer.helpscout.com"},
    {"name": "Gorgias", "category": "Support", "hint_url": "https://developers.gorgias.com"},
    {"name": "Gladly", "category": "Support", "hint_url": "https://developer.gladly.com"},

    # Comms (10)
    {"name": "Slack", "category": "Comms", "hint_url": "https://api.slack.com/docs"},
    {"name": "Twilio", "category": "Comms", "hint_url": "https://www.twilio.com/docs"},
    {"name": "Zoho Cliq", "category": "Comms", "hint_url": "https://www.zoho.com/cliq/help/restapi/v2/"},
    {"name": "Lark", "category": "Comms", "hint_url": "https://open.larksuite.com/document"},
    {"name": "Pumble", "category": "Comms", "hint_url": "https://pumble.com/help/integrations/"},
    {"name": "Discord", "category": "Comms", "hint_url": "https://discord.com/developers/docs"},
    {"name": "Telegram", "category": "Comms", "hint_url": "https://core.telegram.org/bots/api"},
    {"name": "WhatsApp Business", "category": "Comms", "hint_url": "https://developers.facebook.com/docs/whatsapp"},
    {"name": "Aircall", "category": "Comms", "hint_url": "https://developer.aircall.io/api-references/"},
    {"name": "Vonage", "category": "Comms", "hint_url": "https://developer.vonage.com"},

    # Marketing/Ads/Email/Social (10)
    {"name": "Google Ads", "category": "Marketing & Ads", "hint_url": "https://developers.google.com/google-ads/api/docs"},
    {"name": "Meta Ads", "category": "Marketing & Ads", "hint_url": "https://developers.facebook.com/docs/marketing-apis"},
    {"name": "LinkedIn Ads", "category": "Marketing & Ads", "hint_url": "https://learn.microsoft.com/en-us/linkedin/marketing/"},
    {"name": "GoHighLevel", "category": "Marketing & Ads", "hint_url": "https://highlevel.stoplight.io/docs/integrations"},
    {"name": "Mailchimp", "category": "Marketing & Ads", "hint_url": "https://mailchimp.com/developer/marketing/api/"},
    {"name": "Klaviyo", "category": "Marketing & Ads", "hint_url": "https://developers.klaviyo.com/en/reference/api_overview"},
    {"name": "systeme.io", "category": "Marketing & Ads", "hint_url": "https://systeme.io/api"},
    {"name": "Pinterest", "category": "Marketing & Ads", "hint_url": "https://developers.pinterest.com/docs/api/v5/"},
    {"name": "Threads", "category": "Marketing & Ads", "hint_url": "https://developers.facebook.com/docs/threads"},
    {"name": "SendGrid", "category": "Marketing & Ads", "hint_url": "https://docs.sendgrid.com/api-reference"},

    # Ecommerce (10)
    {"name": "Shopify", "category": "Ecommerce", "hint_url": "https://shopify.dev/docs/api"},
    {"name": "WooCommerce", "category": "Ecommerce", "hint_url": "https://woocommerce.github.io/woocommerce-rest-api-docs/"},
    {"name": "BigCommerce", "category": "Ecommerce", "hint_url": "https://developer.bigcommerce.com/docs"},
    {"name": "Salesforce Commerce Cloud", "category": "Ecommerce", "hint_url": "https://developer.salesforce.com/docs/commerce/pwa-kit-managed-runtime/"},
    {"name": "Magento", "category": "Ecommerce", "hint_url": "https://developer.adobe.com/commerce/webapi/"},
    {"name": "Squarespace", "category": "Ecommerce", "hint_url": "https://developers.squarespace.com"},
    {"name": "Ecwid", "category": "Ecommerce", "hint_url": "https://api-docs.ecwid.com"},
    {"name": "Gumroad", "category": "Ecommerce", "hint_url": "https://app.gumroad.com/api"},
    {"name": "Amazon Selling Partner", "category": "Ecommerce", "hint_url": "https://developer-docs.amazon.com/sp-api/docs"},
    {"name": "fanbasis", "category": "Ecommerce", "hint_url": "https://fanbasis.com"},

    # Data/SEO/Scraping (10)
    {"name": "DataForSEO", "category": "Data & SEO", "hint_url": "https://docs.dataforseo.com"},
    {"name": "SE Ranking", "category": "Data & SEO", "hint_url": "https://seranking.com/api.html"},
    {"name": "Ahrefs", "category": "Data & SEO", "hint_url": "https://docs.ahrefs.com/docs/ahrefs-api"},
    {"name": "MrScraper", "category": "Data & SEO", "hint_url": "https://mrscraper.com/docs"},
    {"name": "Apify", "category": "Data & SEO", "hint_url": "https://docs.apify.com/api/v2"},
    {"name": "Firecrawl", "category": "Data & SEO", "hint_url": "https://docs.firecrawl.dev"},
    {"name": "Bright Data", "category": "Data & SEO", "hint_url": "https://docs.brightdata.com"},
    {"name": "Sherlock", "category": "Data & SEO", "hint_url": "https://sherlock-project.github.io"},
    {"name": "Waterfall.io", "category": "Data & SEO", "hint_url": "https://waterfall.io/api"},
    {"name": "Clay", "category": "Data & SEO", "hint_url": "https://clay.com/api"},

    # Dev/Infra (10)
    {"name": "GitHub", "category": "Dev & Infra", "hint_url": "https://docs.github.com/en/rest"},
    {"name": "Vercel", "category": "Dev & Infra", "hint_url": "https://vercel.com/docs/rest-api"},
    {"name": "Netlify", "category": "Dev & Infra", "hint_url": "https://docs.netlify.com/api/get-started/"},
    {"name": "Cloudflare", "category": "Dev & Infra", "hint_url": "https://developers.cloudflare.com/api"},
    {"name": "Supabase", "category": "Dev & Infra", "hint_url": "https://supabase.com/docs/reference"},
    {"name": "Neo4j", "category": "Dev & Infra", "hint_url": "https://neo4j.com/docs/api/"},
    {"name": "Snowflake", "category": "Dev & Infra", "hint_url": "https://docs.snowflake.com/en/developer"},
    {"name": "MongoDB Atlas", "category": "Dev & Infra", "hint_url": "https://www.mongodb.com/docs/atlas/api/"},
    {"name": "Datadog", "category": "Dev & Infra", "hint_url": "https://docs.datadoghq.com/api/"},
    {"name": "Sentry", "category": "Dev & Infra", "hint_url": "https://docs.sentry.io/api/"},

    # Productivity (10)
    {"name": "Notion", "category": "Productivity", "hint_url": "https://developers.notion.com"},
    {"name": "Airtable", "category": "Productivity", "hint_url": "https://airtable.com/developers/web/api/introduction"},
    {"name": "Linear", "category": "Productivity", "hint_url": "https://developers.linear.app/docs"},
    {"name": "Jira", "category": "Productivity", "hint_url": "https://developer.atlassian.com/server/jira/platform/rest-apis/"},
    {"name": "Asana", "category": "Productivity", "hint_url": "https://developers.asana.com/docs"},
    {"name": "Monday.com", "category": "Productivity", "hint_url": "https://developer.monday.com/api-reference"},
    {"name": "ClickUp", "category": "Productivity", "hint_url": "https://clickup.com/api"},
    {"name": "Coda", "category": "Productivity", "hint_url": "https://coda.io/developers/apis/v1"},
    {"name": "Smartsheet", "category": "Productivity", "hint_url": "https://smartsheet.redoc.ly"},
    {"name": "Harvest", "category": "Productivity", "hint_url": "https://help.getharvest.com/api-v2/"},

    # Finance (10)
    {"name": "Stripe", "category": "Finance", "hint_url": "https://stripe.com/docs/api"},
    {"name": "Plaid", "category": "Finance", "hint_url": "https://plaid.com/docs/api/"},
    {"name": "Binance", "category": "Finance", "hint_url": "https://binance-docs.github.io/apidocs"},
    {"name": "Paygent Connect", "category": "Finance", "hint_url": "https://www.nmi.com/developer/"},
    {"name": "iPayX", "category": "Finance", "hint_url": "https://www.ipayx.com/api"},
    {"name": "QuickBooks", "category": "Finance", "hint_url": "https://developer.intuit.com/app/developer/qbo/docs/api/accounting"},
    {"name": "Xero", "category": "Finance", "hint_url": "https://developer.xero.com/documentation/api/"},
    {"name": "Brex", "category": "Finance", "hint_url": "https://developer.brex.com"},
    {"name": "Ramp", "category": "Finance", "hint_url": "https://docs.ramp.com/developer-guide"},
    {"name": "PitchBook", "category": "Finance", "hint_url": "https://pitchbook.com/news/pitchbook-api"},

    # AI/Research/Media (10)
    {"name": "NotebookLM", "category": "AI & Research", "hint_url": "https://ai.google.dev/gemini-api/docs"},
    {"name": "Otter AI", "category": "AI & Research", "hint_url": "https://otter.ai/api"},
    {"name": "Fathom", "category": "AI & Research", "hint_url": "https://fathom.video/api"},
    {"name": "Consensus", "category": "AI & Research", "hint_url": "https://consensus.app/home/blog/"},
    {"name": "Reducto", "category": "AI & Research", "hint_url": "https://reducto.ai/docs"},
    {"name": "Devin", "category": "AI & Research", "hint_url": "https://docs.cognition.ai"},
    {"name": "higgsfield", "category": "AI & Research", "hint_url": "https://higgsfield.ai/docs"},
    {"name": "Mermaid CLI", "category": "AI & Research", "hint_url": "https://github.com/mermaid-js/mermaid-cli"},
    {"name": "YouTube Transcript", "category": "AI & Research", "hint_url": "https://transcriptapi.com"},
    {"name": "Grain", "category": "AI & Research", "hint_url": "https://grain.com/developers"},
]

# Categories for stratified sampling
CATEGORIES = list(set(a["category"] for a in APPS))
