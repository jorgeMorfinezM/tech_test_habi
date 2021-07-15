#!/bin/sh

# Para ejecutar los 3 scripts de unittest del microservicio:

python3 -m unittest -v tests.BaseCase

python3 -m unittest -v tests.UserAuthenticationTest.TestUserLogin

python3 -m unittest -v tests.ManagePropertyTest.TestManageProperty