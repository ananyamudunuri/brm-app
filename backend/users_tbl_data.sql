-- public.users definition

-- Drop table

-- DROP TABLE public.users;

CREATE TABLE public.users (
	id uuid NOT NULL,
	email varchar(255) NOT NULL,
	username varchar(100) NOT NULL,
	password_hash varchar(255) NOT NULL,
	full_name varchar(255) NULL,
	roles text NULL,
	is_active bool NULL,
	is_verified bool NULL,
	created_at timestamptz DEFAULT now() NULL,
	updated_at timestamptz NULL,
	last_login timestamptz NULL,
	CONSTRAINT users_pkey PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);
CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);

INSERT INTO public.users
(id, email, username, password_hash, full_name, roles, is_active, is_verified, created_at, updated_at, last_login)
VALUES('3b17067c-6b20-454a-a5c6-b23212f401e9'::uuid, 'user@example.com', 'user', '$2b$12$zvpyZLClf4.TGhlKX.7IjOSzxfW22mfEfJRy/bOdPjMJ3TzRA35J.', 'Regular User', 'user', true, true, '2026-05-07 14:18:18.410', NULL, NULL);
INSERT INTO public.users
(id, email, username, password_hash, full_name, roles, is_active, is_verified, created_at, updated_at, last_login)
VALUES('933ee311-331c-4b95-9e19-2c08087e995b'::uuid, 'ananya@meridiansoft.com', 'ananya', '$2b$12$ytQfrspA4A.sAgXdLLBjX.1rLT4RJPmC9FR7nJKQS9R6gvEPx5p9a', 'Ananya', 'user', true, true, '2026-05-07 16:04:47.541', NULL, NULL);
INSERT INTO public.users
(id, email, username, password_hash, full_name, roles, is_active, is_verified, created_at, updated_at, last_login)
VALUES('936d0fc0-af67-4cf9-8f68-fe1f50442a70'::uuid, 'admin@example.com', 'admin', '$2b$12$HLkES3tCuxLmg7ofZvvcauZ7oiXzWXakwHCTQEZl6BU9Z0nh62FMG', 'System Administrator', 'admin', true, true, '2026-05-07 14:18:18.410', '2026-05-07 17:55:36.181', '2026-05-07 17:55:36.475');