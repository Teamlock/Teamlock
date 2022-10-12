from apps.secret.schema import CreateLoginSchema, SecretValueSchema
from apps.workspace.schema import ImportXMLFileSchema
from toolkits.workspace import WorkspaceUtils
from apps.workspace.models import Workspace
from apps.folder.models import Folder
from apps.secret.models import Login
import xml.etree.ElementTree as ET
from apps.user.models import User
from settings import settings
import logging.config
import traceback
import logging
import json

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")


class ImportUtils(WorkspaceUtils):
  @classmethod
  def create_secret_import(
      cls,
      import_schema: ImportXMLFileSchema,
      name: str,
      url: str,
      login: str,
      password: str,
      informations: str,
      sym_key: str,
      folder: Folder | None,
      user: User
  ) -> Login:
      secret_def: CreateLoginSchema = CreateLoginSchema(
          name=SecretValueSchema(
              encrypted=import_schema.encrypt_name,
              value=name
          ),
          url=SecretValueSchema(
              encrypted=import_schema.encrypt_url,
              value=url
          ),
          login=SecretValueSchema(
              encrypted=import_schema.encrypt_login,
              value=login
          ),
          password=SecretValueSchema(
              encrypted=True,
              value=password
          ),
          informations=SecretValueSchema(
              encrypted=import_schema.encrypt_informations,
              value=informations
          ),
          secret_type="login"
      )

      secret = WorkspaceUtils.encrypt_secret(user, sym_key, secret_def)
      secret.folder = folder
      secret.created_by = user.in_db
      secret.updated_by = user.in_db
      return secret

  @classmethod
  def import_teamlock_backup(
      cls,
      user: User,
      workspace: Workspace,
      sym_key: str,
      import_schema: ImportXMLFileSchema,
      file: str
  ):
      file = json.loads(file)

      def save_folders(user, folders, parent=None):
          for tmp_folder in folders:
              folder = Folder.objects.create(
                  workspace=workspace,
                  name=tmp_folder["name"],
                  icon="mdi-folder",
                  created_by=user.in_db.pk,
                  parent=parent
              )

              keys: list = []
              for tmp_key in tmp_folder['keys']:
                  url = tmp_key.get("uri", "") or tmp_key.get("ipv4", "") or tmp_key.get("ipv6", "")
                  if url is None:
                      url = ""

                  keys.append(cls.create_secret_import(
                      import_schema,
                      tmp_key["name"] or "",
                      url,
                      tmp_key.get("login", "") or "",
                      tmp_key.get("password", "") or "",
                      tmp_key.get("informations", "") or "",
                      sym_key,
                      folder,
                      user
                  ))

              if len(keys) > 0:
                  Login.objects.insert(keys)

              save_folders(user, tmp_folder["childs"], folder)

      try:
          save_folders(user, file)
          workspace.import_in_progress = False
          workspace.save()

          logger.info(
              f"[IMPORT][{str(workspace.pk)}][{workspace.name}] Import finished"
          )
      except Exception as error:
          logger.critical(error)
          workspace.import_in_progress = False
          workspace.save()

  @classmethod
  def import_xml_keepass(
      cls,
      user: User,
      workspace: Workspace,
      sym_key: str,
      import_schema: ImportXMLFileSchema,
      file: str
  ):
      secret_mapping = {
          'Password': 'password',
          'Title': 'name',
          'URL': 'url',
          'UserName': 'login',
          'Notes': 'informations'
      }

      def save_xml_folder(user, group, parent=None):
          for subgroup in group.findall("Group"):
              group_name = subgroup.find("Name").text

              folder = Folder.objects.create(
                  workspace=workspace,
                  name=group_name,
                  icon="mdi-folder",
                  created_by=user.in_db.pk,
                  parent=parent
              )

              secrets: list = []
              for entry in subgroup.findall("Entry"):
                  tmp: dict = {}
                  for entry_value in entry.findall("String"):
                      key: str = entry_value.find("Key").text
                      value: str = entry_value.find("Value").text

                      if key in secret_mapping.keys():
                          if value:
                              tmp[secret_mapping[key]] = value
                          else:
                              tmp[secret_mapping[key]] = ""

                  secrets.append(cls.create_secret_import(
                      import_schema,
                      tmp["name"],
                      tmp["url"],
                      tmp["login"],
                      tmp["password"],
                      tmp["informations"],
                      sym_key,
                      folder,
                      user
                  ))

              if len(secrets) > 0:
                  Login.objects.insert(secrets)

              save_xml_folder(user, subgroup, folder)

      try:
          xml_file = ET.fromstring(file)
          racine = xml_file.find('Root').find('Group')
          save_xml_folder(user, racine)

          workspace.import_in_progress = False
          workspace.save()

          logger.info(
              f"[IMPORT][{str(workspace.pk)}][{workspace.name}] Import finished"
          )

      except Exception as error:
        tb = traceback.format_exc()
        logger.critical(error)
        workspace.import_in_progress = False
        workspace.import_error = tb
        workspace.save()

  @classmethod
  def import_json_bitwarden(
      cls,
      user: User,
      workspace: Workspace,
      sym_key: str,
      import_schema: ImportXMLFileSchema,
      file: str
  ):
      file = json.loads(file)

      folders: dict = {}
      folders_mapping: dict = {}
      # Prepare tree

      root_folder = Folder.objects.create(
          workspace=workspace,
          created_by=user.in_db,
          icon="mdi-folder",
          name="Others"
      )

      def save_folder(bitwarden_pk: str, folder_name: str, parent=None):
          folder = Folder(
              workspace=workspace,
              created_by=user.in_db,
              icon="mdi-folder",
              name=folder_name,
              parent=parent
          )

          folder.save()
          folders[bitwarden_pk] = folder.pk
          folders_mapping[folder_name] = folder.pk

      try:
          for tmp_f in file["folders"]:
              tmp_name = tmp_f["name"].split("/")
              for i, tmp_n in enumerate(tmp_name):
                  if i == 0:
                      if not folders_mapping.get(tmp_n):
                          save_folder(tmp_f['id'], tmp_n)
                  else:
                      save_folder(tmp_f['id'], tmp_n, folders_mapping[tmp_name[i-1]])

          keys: list = []
          for item in file["items"]:
              folder = folders.get(item["folderId"], root_folder)
              login = item["login"]["username"] or ""
              secret = item["login"]["password"] or ""
              name = item["name"] or ""
              informations = item["notes"] or ""
              url = item["login"].get("uris", [{}])[0].get("uri", "")

              keys.append(cls.create_secret_import(
                  import_schema,
                  name,
                  url,
                  login,
                  secret,
                  informations,
                  sym_key,
                  folder,
                  user
              ))
          
          if len(keys) > 0:
              Login.objects.insert(keys)

          workspace.import_in_progress = False
          workspace.save()

          logger.info(
              f"[IMPORT][{str(workspace.pk)}][{workspace.name}] Import finished"
          )
      except Exception as error:
          logger.critical(error)
          workspace.import_in_progress = False
          workspace.save()
