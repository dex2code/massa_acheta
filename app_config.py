app_config = {}
app_config['telegram']  = {}
app_config['service']   = {}


# Telegram settings
app_config['telegram']['sending_delay_sec'] = 2
app_config['telegram']['sending_timeout_sec'] = 5


# Service settings
app_config['service']['results_path'] = "app_results.json"
app_config['service']['deferred_credits_path'] = "deferred_credits.json"
app_config['service']['stat_path'] = "app_stat.json"
app_config['service']['public_dir_path'] = 'public_dir.json'

app_config['service']['main_loop_period_min'] = 10
app_config['service']['heartbeat_period_hours'] = 6
app_config['service']['massa_network_update_period_min'] = 30

app_config['service']['http_session_timeout_sec'] = 300
app_config['service']['http_probe_timeout_sec'] = 120

app_config['service']['massa_release_url'] = "https://api.github.com/repos/massalabs/massa/releases/latest"
app_config['service']['acheta_release_url'] = "https://api.github.com/repos/dex2code/massa_acheta/releases/latest"

app_config['service']['mainnet_rpc_url'] = "https://mainnet.massa.net/api/v2"
app_config['service']['mainnet_explorer_url'] = "https://explorer.massa.net/mainnet"
app_config['service']['massexplo_api_url'] = "https://api.massexplo.io/info?network=MainNet"

app_config['service']['mainnet_stakers_bundle'] = 1000
