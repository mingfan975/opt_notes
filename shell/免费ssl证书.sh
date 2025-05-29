#! /bin/bash

# ACCOUNT_THUMBPRINT='xxxxxxx'
function install_acme() {
  if [ ! -f '/root/.acme.sh/acme.sh' ]; then
    curl https://get.acme.sh | sh -s email=xxx@163.com
    alias acme.sh=/root/.acme.sh/acme.sh
    echo 'alias acme.sh=/root/.acme.sh/acme.sh' >>/etc/profile
    source /etc/profile
  fi
}

function create_default_conf() {
  if [ ! -f "/etc/nginx/conf.d/default.conf" ]; then
    cat >/etc/nginx/conf.d/default.conf <<EOF
  server {
          listen 80 default_server;
          listen [::]:80 default_server;
          root /var/www/html;

          index index.html;

          server_name _;

          location / {
                  try_files \$uri \$uri/ =404;
          }
        }
EOF
  fi
}

function create_ldy_nginx_conf() {
  domain=$1
  pt=$2
  if [ ! -f "/etc/nginx/conf.d/${domain}.conf" ]; then

    file="/etc/nginx/conf.d/${domain}.conf"
    cat >"$file" <<EOF
  server {
    listen 443 ssl;
    server_name ${domain};

    client_max_body_size 100m; # 录像及文件上传大小限制

    ssl_certificate  /etc/nginx/cert/${domain}.cer;
    ssl_certificate_key /etc/nginx/cert/${domain}.key;
    ssl_session_timeout 5m;
    ssl_protocols SSLv3 TLSv1.1 TLSv1.2;
    ssl_ciphers ALL:!ADH:!EXPORT56:RC4+RSA:+HIGH:+MEDIUM:+LOW:+SSLv2:+EXP;
    ssl_prefer_server_ciphers on;
    set \$req_id hka.\$pid.\$msec.\$remote_addr.\$connection.\$connection_requests;
    proxy_set_header X-Request-Id \$req_id;
    location / {
        proxy_redirect off;
        resolver 8.8.8.8 ipv6=off;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$http_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_connect_timeout 30;
        proxy_send_timeout 60;
        proxy_read_timeout 60;
        proxy_pass http://${pt};
        add_header Cache-Control max-age=300s;
        proxy_cache_valid 1d;
        proxy_ignore_headers Set-Cookie Cache-Control;
        proxy_hide_header Cache-Control;
        proxy_hide_header Set-Cookie;
        add_header cache \$upstream_cache_status;
        proxy_cache_key \$host\$uri\$is_args\$args\$http_user_agent;
    }

    location ^~ /web {
        proxy_pass https://douyin-videos-01.sgp1.digitaloceanspaces.com;
    }
    location = /favicon.ico {
        log_not_found off;
        access_log off;
    }
}
EOF
  fi
}

function create_web_index() {
  web_index='/var/www/html/index.html'
  if [ ! -f "${web_index}" ]; then
    touch "${web_index}" && echo 'nginx test' >"${web_index}"
  fi
}

# create_cert domain
function create_cert() {
  domain=$1
  ngx_file="/etc/nginx/conf.d/${domain}.conf"
  if [ ! -f "${ngx_file}" ]; then
    touch "${ngx_file}"
  fi
  key="/etc/nginx/cert/${domain}.key"
  if [ ! -f "${key}" ]; then
    touch "${key}"
  fi
  chain="/etc/nginx/cert/${domain}.cer"
  if [ ! -f "${chain}" ]; then
    touch "${chain}"
  fi

  sudo /root/.acme.sh/acme.sh --issue -d "${domain}" --log --webroot /var/www/html/
  sudo /root/.acme.sh/acme.sh --installcert -d "${domain}" --key-file "${key}" --fullchain-file "${chain}"
  if [ $? -eq 0 ]; then
    if [ -f "${ngx_file}" ]; then
      sed -i "s#ssl_certificate .*;#ssl_certificate  ${chain};#g" "${ngx_file}"
      sed -i "s#ssl_certificate_key  .*;#ssl_certificate_key  ${key};#" "${ngx_file}"
    else
      echo "${ngx_file} not exist"
    fi
  fi
}

function main() {
  create_ldy_nginx_conf $1 $2
  install_acme
  create_default_conf
  create_web_index
  create_cert $1
}

if [[ $# -eq 2 ]]; then
  main "$1" "$2"
else
  echo 'Usage: bash $0 domain_name platform_name'
fi
nginx -t && nginx -s reload
