#!/usr/bin/python

"""This file is part of Teamlock.
Teamlock is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Teamlock is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Teamlock.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Olivier de Régis"
__credits__ = []
__license__ = "GPLv3"
__version__ = "3.0.0"
__maintainer__ = "Teamlock Project"
__email__ = "contact@teamlock.io"
__doc__ = ''

from password_strength import PasswordPolicy, PasswordStats
from pydantic import BaseModel
from settings import settings



class PasswordPolicySchema(BaseModel):
    length: int = 12
    uppercase: int = 1
    numbers: int = 1
    special: int = 1

    def stats(self, password: str) -> float:
        stats: PasswordStats = PasswordStats(password)
        result: float = stats.strength()
        return result

    def verify(self, password: str) -> list:
        policy: PasswordPolicy = PasswordPolicy.from_names(**self.dict())
        result: list = policy.test(password)
   
        errors: list = []
        for res in result:
            name: str = res.name()
            min_value: int = getattr(self, name)

            errors.append({
                "type": name,
                "min": min_value
            })
        
        return errors


class ConfigSchema(BaseModel):
    version: float = settings.VERSION
    rsa_key_size: int = 4096
    password_duration: int = 100
    password_policy: PasswordPolicySchema = PasswordPolicySchema()
    allow_self_registration: bool = False
    allowed_email_addresses: list[str] = []
    
    class Config:
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
