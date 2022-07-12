TeamLock
===================================

TeamLock is a passwords manager for Enterprises. 

### Security

To manage the security of passwords, this app uses two different encryption mecanism:
- Asymetric encryption with RSA
- Symetric encryption

When a user is created, a mail is sent to allow him to configurate his account. He will have to choose a password for login and for asymetric key generation.

Once all the password are saved, the app will encrypt the database with a symetric key.
Then, the symetric key is encrypted using the user public key.

## Installation

    # Edit docker-compose.yml and fill the environnment variable
    # SMTP is mandatory to send registration email to users

    $ docker-compose up -d
    # Go to http://ip/#/install

## Licence

Teamlock is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Teamlock is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Teamlock. If not, see <http://www.gnu.org/licenses/>.

## More Information

- Author: Olivier de Régis
- License: GPL 3.0