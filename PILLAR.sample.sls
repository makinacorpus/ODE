{% set domain = 'ode_api.localhost' %}

makina-states.projects.ode_api:
  db_name: ode
  db_user: ode
  db_password: ode
  port: 8002
  circus_port: 56555
  domain: {{ domain }}
  from_email: noreply@{{ domain }}
  admins:
    - admin@{{ domain }}