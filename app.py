from flask import Flask, render_template_string, request, redirect, url_for, flash
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()  

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "cambiame")

DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    print("⚠️  NO SE ENCONTRÓ DATABASE_URL en variables de entorno.")
    print("Define DATABASE_URL con tu URI de Neon antes de ejecutar la app.")

TEMPLATE = """
<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <title>Northwind - Verificador</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  </head>
  <body class="bg-light">
    <div class="container my-4">
      <h1 class="mb-3">✅ Verificador Northwind</h1>
      {% if not db_ok %}
        <div class="alert alert-danger">No se encontró DATABASE_URL. Configure la variable de entorno.</div>
      {% endif %}
      <div class="mb-3">
        <form method="post" action="{{ url_for('run_action') }}">
          <div class="btn-group" role="group">
            <button name="action" value="ver_vistas" class="btn btn-outline-primary">1. Ver Vistas</button>
            <button name="action" value="ver_procedures" class="btn btn-outline-primary">2. Ver Procedures</button>
            <button name="action" value="probar_vistas" class="btn btn-outline-success">3. Probar Vistas</button>
            <button name="action" value="probar_procedures" class="btn btn-outline-success">4. Probar Procedures</button>
          </div>
        </form>
      </div>

      {% with messages = get_flashed_messages() %}
        {% if messages %}
          {% for m in messages %}
            <div class="alert alert-info">{{ m }}</div>
          {% endfor %}
        {% endif %}
      {% endwith %}

      {% if sql %}
        <div class="card mb-3">
          <div class="card-header"><strong>SQL ejecutado</strong></div>
          <div class="card-body"><pre>{{ sql }}</pre></div>
        </div>
      {% endif %}

      {% if rows is not none %}
        <div class="card">
          <div class="card-header"><strong>Resultados ({{ rows|length }} filas)</strong></div>
          <div class="card-body p-0">
            <div style="overflow:auto">
              <table class="table table-sm table-striped mb-0">
                <thead class="table-light">
                  <tr>
                    {% for c in columns %}
                      <th>{{ c }}</th>
                    {% endfor %}
                  </tr>
                </thead>
                <tbody>
                  {% for r in rows %}
                    <tr>
                      {% for c in columns %}
                        <td>{{ r[c] }}</td>
                      {% endfor %}
                    </tr>
                  {% endfor %}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      {% endif %}

    </div>
  </body>
</html>
"""

def get_conn():
    if not DB_URL:
        raise RuntimeError("DATABASE_URL no definida")
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

@app.route("/", methods=["GET"])
def index():
    return render_template_string(TEMPLATE, db_ok=bool(DB_URL), rows=None, columns=None, sql=None)

@app.route("/run", methods=["POST"])
def run_action():
    action = request.form.get("action")
    sql = None

    if action == "ver_vistas":
        sql = """
            SELECT table_name AS vista, table_type AS tipo
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'VIEW'
            ORDER BY table_name;
        """
    elif action == "ver_procedures":
        sql = """
            SELECT routine_name AS procedimiento, routine_type AS tipo
            FROM information_schema.routines
            WHERE routine_schema = 'public'
            ORDER BY routine_name;
        """
    elif action == "probar_vistas":
        sql = "SELECT * FROM VistaPedidosDetalles LIMIT 10;"
    elif action == "probar_procedures":
        sql = "SELECT * FROM sp_historial_pedidos_cliente(1) LIMIT 5;"

    if not sql:
        flash("Acción no reconocida")
        return redirect(url_for("index"))

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cols = rows[0].keys() if rows else []
        cur.close()
        conn.close()
        return render_template_string(TEMPLATE, db_ok=True, rows=rows, columns=cols, sql=sql)
    except Exception as e:
        flash(f"Error al ejecutar: {e}")
        return render_template_string(TEMPLATE, db_ok=bool(DB_URL), rows=None, columns=None, sql=sql)

if __name__ == "__main__":
    # correr local: http://127.0.0.1:5000
    app.run(host="0.0.0.0", port=5000, debug=True)
