use minijinja::{Environment, context};
use serde_json::Value;

pub fn render_index(metrics: &Value) -> anyhow::Result<String> {
    let mut env = Environment::new();
    env.add_template("index", include_str!("../templates/index.html"))?;
    let tmpl = env.get_template("index")?;
    Ok(tmpl.render(context! { metrics })?)
}

pub fn render_dashboard(metrics: &Value, agent_stats: &Value) -> anyhow::Result<String> {
    let mut env = Environment::new();
    env.add_template("dashboard", include_str!("../templates/dashboard.html"))?;
    let tmpl = env.get_template("dashboard")?;
    Ok(tmpl.render(context! { metrics, agent_stats })?)
}
