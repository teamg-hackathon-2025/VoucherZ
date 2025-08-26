provider "aws" {
  region = "ap-northeast-1" 
} 


## NAT GateWay作成
# 1. サブネット取得（ネームタグでフィルタ）
data "aws_subnet" "public_subnet" {
  filter {
    name   = "tag:Name"
    values = ["alb-voucherz-test-subnet-public1-ap-northeast-1a"]
  }
}

# 2. Elastic IP（VPC用）
resource "aws_eip" "nat" {
  domain = "vpc"
  tags = {
    Name = "nat-voucherz-test-eip"
  }
}

# 3. NAT Gateway（パブリック接続）
resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = data.aws_subnet.public_subnet.id
  connectivity_type = "public"  # パブリック接続
  tags = {
    Name = "nat-voucherz-test"
  }
}


# 既存のルートテーブルを参照
data "aws_route_table" "private_rtb" {
  filter {
    name   = "tag:Name"
    values = ["fargate-voucherz-test-rtb-private-ap-northeast-1a"]
  }
}

data "aws_route_table" "private_rtb_1c" {
  filter {
    name   = "tag:Name"
    values = ["fargate-voucherz-test-rtb-private2-ap-northeast-1c"]
  }
}

# NAT Gatewayへのルートを追加
resource "aws_route" "private_nat_route" {
  route_table_id         = data.aws_route_table.private_rtb.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat.id
}

resource "aws_route" "private_nat_route_1c" {
  route_table_id         = data.aws_route_table.private_rtb_1c.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat.id
}
## ALB作成
# ==============================
# VPC
# ==============================
data "aws_vpc" "voucherz_test" {
  filter {
    name   = "tag:Name"
    values = ["voucherz-test-vpc"]
  }
}

# ==============================
# Subnets
# ==============================
data "aws_subnet" "public1" {
  filter {
    name   = "tag:Name"
    values = ["alb-voucherz-test-subnet-public1-ap-northeast-1a"]
  }
}

data "aws_subnet" "public2" {
  filter {
    name   = "tag:Name"
    values = ["alb-voucherz-test-subnet-public2-ap-northeast-1c"]
  }
}

# ==============================
# Security Group
# ==============================
data "aws_security_group" "alb_sg" {
  filter {
    name   = "tag:Name"
    values = ["alb-sg-voucherz-test"]
  }
  vpc_id = data.aws_vpc.voucherz_test.id
}

# ==============================
# Target Group
# ==============================
data "aws_lb_target_group" "fargate_tg" {
  name = "fargate-tg-voucherz-test"
}

# ==============================
# Application Load Balancer
# ==============================
resource "aws_lb" "alb_voucherz_test" {
  name               = "alb-voucherz-test"
  load_balancer_type = "application"
  internal           = false
  ip_address_type    = "ipv4"

  security_groups = [data.aws_security_group.alb_sg.id]
  subnets         = [
    data.aws_subnet.public1.id,
    data.aws_subnet.public2.id
  ]

  tags = {
    Name = "alb-voucherz-test"
  }
}

# 発行済みACM証明書を取得
data "aws_acm_certificate" "voucherz" {
  domain   = "voucherz.jp"
}

# ==============================
# Listener (HTTPS :443)
# ==============================
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.alb_voucherz_test.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = data.aws_acm_certificate.voucherz.arn 

  default_action {
    type             = "forward"
    target_group_arn = data.aws_lb_target_group.fargate_tg.arn
  }
}


# 既存ホストゾーンを取得
data "aws_route53_zone" "voucherz" {
  name         = "voucherz.jp."
  private_zone = false
}

# Route53にAレコード（エイリアス）作成
resource "aws_route53_record" "voucherz_root_alias" {
  zone_id = data.aws_route53_zone.voucherz.zone_id
  name    = ""                        # 空欄 = ルートドメイン
  type    = "A"

  alias {
    name                   = aws_lb.alb_voucherz_test.dns_name
    zone_id                = aws_lb.alb_voucherz_test.zone_id
    evaluate_target_health = true
  }

}


# サブネット
data "aws_subnet" "private_subnet" {
  filter {
    name   = "tag:Name"
    values = ["fargate-voucherz-test-subnet-private2-ap-northeast-1a"]
  }
}

data "aws_subnet" "private_subnet_1c" {
filter {
  name   = "tag:Name"
  values = ["fargate-voucherz-test-subnet-private2-ap-northeast-1c"]
}
}

# セキュリティグループ
data "aws_security_group" "fargate_sg" {
  filter {
    name   = "tag:Name"
    values = ["fargate-sg-voucherz-test"]
  }
  vpc_id = data.aws_vpc.voucherz_test.id
}

# リスナー
#data "aws_lb_listener" "listener" {
#  load_balancer_arn = aws_lb.alb_voucherz_test.arn
#  port              = 443
#}

# 既存 ECS クラスタ
data "aws_ecs_cluster" "this" {
  cluster_name = "voucherz-test"
}

# 既存 ECS タスク定義（最新リビジョンを取得）
data "aws_ecs_task_definition" "nginx" {
  task_definition = "voucherz-test-nginx-taskdef"
}

# 既存 Cloud Map ネームスペース (service.local)
#data "aws_service_discovery_private_dns_namespace" "namespace" {
#  name = "service.local"
#}
resource "aws_service_discovery_private_dns_namespace" "namespace" {
  name = "service.local"
  vpc  = data.aws_vpc.voucherz_test.id
  lifecycle {
    prevent_destroy = true
  }
}

# 既存 Cloud Map サービス (django)
data "aws_service_discovery_service" "django" {
  name         = "django"
  namespace_id = aws_service_discovery_private_dns_namespace.namespace.id
}


# 既存 ECS タスク定義（最新リビジョン）
data "aws_ecs_task_definition" "django" {
  task_definition = "voucherz-test-django-taskdef"
}

############################
# ECS サービス
############################
# django
resource "aws_ecs_service" "django" {
  name            = "voucherz-test-django-service"
  cluster         = data.aws_ecs_cluster.this.id
  task_definition = data.aws_ecs_task_definition.django.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [
      data.aws_subnet.private_subnet.id,
      data.aws_subnet.private_subnet_1c.id
    ]
    security_groups = [data.aws_security_group.fargate_sg.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = data.aws_service_discovery_service.django.arn
  }
}

# nginx
resource "aws_ecs_service" "nginx" {
  name            = "voucherz-test-nginx-service"
  cluster         = data.aws_ecs_cluster.this.id
  task_definition = data.aws_ecs_task_definition.nginx.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [
      data.aws_subnet.private_subnet.id,
      data.aws_subnet.private_subnet_1c.id
    ]
    security_groups = [data.aws_security_group.fargate_sg.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = data.aws_lb_target_group.fargate_tg.arn
    container_name   = "nginx"
    container_port   = 80
  }

  depends_on = [aws_lb_listener.https]
}

# RDSのセキュリティグループ
data "aws_security_group" "rds_sg" {
  filter {
    name   = "tag:Name"
    values = ["rds-sg-voucherz-test"]
  }
}


# RDSのサブネットグループ
data "aws_db_subnet_group" "rds_subnet" {
  name = "default-vpc-05ffd3536a22a6d48"
}

# RDS
resource "aws_db_instance" "rds_voucherz_test" {
  identifier              = "rds-voucherz-test"
  engine                  = "mysql"
  instance_class          = "db.t4g.micro"
  allocated_storage       = 20
  storage_type            = "gp2"
  username                = "myappuser"
  password                = "mysecretpassword"
  db_subnet_group_name    = data.aws_db_subnet_group.rds_subnet.name
  vpc_security_group_ids  = [data.aws_security_group.rds_sg.id]
  multi_az                = false
  publicly_accessible     = false
  backup_retention_period = 0
  skip_final_snapshot     = true
  engine_version          = "8.0" # MySQL 最新安定版を指定
  auto_minor_version_upgrade = true
  db_name = "myappdb"
}

# SSM Parameter Store に RDS エンドポイントを登録
resource "aws_ssm_parameter" "mysql_container_endpoint" {
  name  = "/voucherz/MYSQL_CONTAINER_NAME"
  type  = "String"
  value = split(":", aws_db_instance.rds_voucherz_test.endpoint)[0]
}


