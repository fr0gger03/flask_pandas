#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER inventorydbuser WITH ENCRYPTED PASSWORD 'password';
	CREATE DATABASE INVENTORYDB;
	GRANT ALL PRIVILEGES ON DATABASE INVENTORYDB TO inventorydbuser;
	\connect "inventorydb";

CREATE SEQUENCE projects_tb_pid_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."projects_tb" (
    "pid" integer DEFAULT nextval('projects_tb_pid_seq') NOT NULL,
    "userid" integer,
    "projectname" character varying(20),
    CONSTRAINT "projects_tb_pkey" PRIMARY KEY ("pid")
) WITH (oids = false);


CREATE SEQUENCE users_tb_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."users_tb" (
    "id" integer DEFAULT nextval('users_tb_id_seq') NOT NULL,
    "username" character varying(20) NOT NULL,
    "password" character varying(180) NOT NULL,
    CONSTRAINT "users_tb_pkey" PRIMARY KEY ("id")
) WITH (oids = false);


CREATE SEQUENCE workloads_tb_vmid_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."workloads_tb" (
    "vmid" integer DEFAULT nextval('workloads_tb_vmid_seq') NOT NULL,
    "pid" integer,
    "mobid" character varying(20),
    "cluster" character varying(40),
    "virtualdatacenter" character varying(40),
    "os" character varying(40),
    "os_name" character varying(40),
    "vmstate" character varying(20),
    "vcpu" integer,
    "vmname" character varying(40),
    "vram" integer,
    "ip_addresses" character varying(60),
    "vinfo_provisioned" numeric(12,6),
    "vinfo_used" numeric(12,6),
    "vmdktotal" numeric(12,6),
    "vmdkused" numeric(12,6),
    "readiops" numeric(12,6),
    "writeiops" numeric(12,6),
    "peakreadiops" numeric(12,6),
    "peakwriteiops" numeric(12,6),
    "readthroughput" numeric(12,6),
    "writethroughput" numeric(12,6),
    "peakreadthroughput" numeric(12,6),
    "peakwritethroughput" numeric(12,6),
    CONSTRAINT "workloads_tb_pkey" PRIMARY KEY ("vmid")
) WITH (oids = false);


ALTER TABLE ONLY "public"."projects_tb" ADD CONSTRAINT "projects_tb_userid_fkey" FOREIGN KEY (userid) REFERENCES users_tb(id) NOT DEFERRABLE;

ALTER TABLE ONLY "public"."workloads_tb" ADD CONSTRAINT "workloads_tb_pid_fkey" FOREIGN KEY (pid) REFERENCES projects_tb(pid) NOT DEFERRABLE;
GRANT ALL ON ALL TABLES IN SCHEMA public TO inventorydbuser;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO inventorydbuser;


EOSQL