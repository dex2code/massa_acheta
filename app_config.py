app_config = {}

app_config['telegram']  = {}
app_config['service']   = {}

app_config['telegram']['service_nickname'] = "MASSA 🦗 Acheta:"
app_config['telegram']['sending_delay_sec'] = 3
app_config['telegram']['sending_timeout_sec'] = 5


app_config['service']['results_path'] = "app_results.json"

app_config['service']['main_loop_period_sec'] = 300

app_config['service']['http_session_timeout_sec'] = 300
app_config['service']['http_probe_timeout_sec'] = 60

app_config['service']['heartbeat_period_hours'] = 4

app_config['service']['massa_release_url'] = "https://api.github.com/repos/massalabs/massa/releases/latest"
app_config['service']['acheta_release_url'] = "https://raw.githubusercontent.com/dex2code/massa_acheta/main/RELEASE"

app_config['service']['mainnet_rpc'] = "https://mainnet.massa.net/api/v2"
app_config['service']['mainnet_explorer'] = "https://explorer.massa.net/mainnet"
