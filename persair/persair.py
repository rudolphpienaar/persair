# Turn off all logging for modules in this libary.
import logging

from pytest import fail

logging.disable(logging.CRITICAL)

# System imports
import      os
import      sys
import      getpass
import      argparse
import      json
import      pprint
import      csv
import      logging
import      datetime

import      asyncio
import      aiohttp
from        aiohttp             import ClientResponse

from        argparse            import  Namespace, ArgumentParser
from        argparse            import  RawTextHelpFormatter
from        loguru              import  logger

from        pfmisc              import  Colors as C

from        pathlib             import  Path

import      pudb
from        typing              import Any, Callable
from        pydantic            import HttpUrl

try:
    from        config          import settings
    from        models          import sensorModel
except:
    from        .config         import settings
    from        .models         import sensorModel


matlogger:logging.Logger    = logging.getLogger('matplotlib')
matlogger.propagate         = False
import      matplotlib
matplotlib.use('Agg')

import      pylab
import      matplotlib.cm       as      cm

LOG             = logger.debug

logger_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> │ "
    "<level>{level: <5}</level> │ "
    "<yellow>{name: >28}</yellow>::"
    "<cyan>{function: <30}</cyan> @"
    "<cyan>{line: <4}</cyan> ║ "
    "<level>{message}</level>"
)
logger.remove()
logger.add(sys.stderr, format=logger_format)


description:str = f"""
    DESCRIPTION

    `persair` is a client application for interacting with the purpleair API
    (https://api.purpleair.com) on behalf of a registered purple air users/
    organizations.

    This is a relatively "simple" app with minimal dependencies and it mostly
    used as means to access data in the purple air API from a command line.

    Note that each call to the purple air API consumes "tokens" that carry an
    actual monetary cost. Once all tokens are exhausted, new tokens need to be
    purchased.

    The companion `pfair` web-based API provides caching of data pulled from the
    purple air API and is recommended for most cases.

"""

package_CLIself = '''
        [--keyStore <key.json>]                                                 \\
        [--projectName <name>]                                                  \\
        [--readKey <readkey>]                                                   \\
        [--writeKey <writekey>]                                                 \\
        [--sensorDataGet <sensorRef>]                                           \\
        [--fieldsList]                                                          \\
        [--fields <comma,separated,list>]                                       \\
        [--asHistory | --asHistoryCSV]                                          \\
        [--start_timestamp <%Y-%m-%d>]                                          \\
        [--end_timestamp <%Y-%m-%d>]                                            \\
        [--sensorRefType sensor_index|sensor_id]                                \\
        [--sensorsAddFromFile <filename>]                                       \\
        [--sensorAddToGroup <sensorRef>]                                        \\
        [--sensorsInGroupList <groupid>]                                        \\
        [--usingGroupID <groupid>]                                              \\
        [--man]                                                                 \\
        [--version]'''

package_argSynopsisSelf = f"""
        [--keyStore <key.json>]
        A json key store file that contains both the read and write keys for the
        purple air API. If used, the --readKey and --writeKey are supefluous.

        [--projectName <projectName>]
        The name of the project in the keyStore (the keyStore can contain many
        key pairs, organized by project).

        [--readKey <readkey>]
        The key to read from the purple air API.

        [--writeKey <writekey>]
        The key to write to the purple air API.

        [--sensorDataGet <sensorRef>]
        Get data for sensor <sensorRef>. This can either be a sensor index
        or a sensor ID. Set the ref type with --sensorRefType.

        [--fieldsList]
        If specified, print information about the fields can be passed to the
        "fields" parameter.

        [--fields <comma,separated,list>]
        A comma separated list of field data to retrieve. Useful if you only want
        a specific measurement and don't want the bloat (and cost) of all the data.

        [--asHistory | --asHistoryCSV]
        If specified, do a "history" retrieve (optionally as CSV data)

        [--start_timestamp <%Y-%m-%d>]
        For a "history" retrieve, the start timestamp.

        [--end_timestamp <%Y-%m-%d>]
        For a "history" retrieve, the end timestamp.

        [--sensorRefType sensor_index|sensor_id]
        Set the specific reference "type" for sensors. This must be one of
        either 'sensor_id' or 'sensor_index'. Default is 'sensor_index'.

        [--sensorAddToGroup <sensorRef>]
        Add the sensor referenced by <sensorRef> to a group. The group is
        additionally specified with the --usingGroupID CLI.

        [--sensorsAddFromFile <filename>]
        Add all sensors referenced in <filename> to the group defined by
        --usingGroupID. References in the <filename> should only contain
        a single sensor per line.

        [--sensorsInGroupList <groupid>]
        List all sensors in <groupid>.

        [--usingGroupID <groupid>]
        CLI for additionally specifying a <groupid> to use in conjunction
        with several sensor operations.

        [--version]
        If specified, print app name/version.

        [--man]
        If specified, print this help/man page.

"""

package_CLIfull             = package_CLIself
package_CLIDS               = package_CLIself
package_argsSynopsisFull    = package_argSynopsisSelf
package_argsSynopsisDS      = package_argSynopsisSelf

def parser_setup(desc:str, add_help:bool = True) -> ArgumentParser:
    parserSelf = ArgumentParser(
                description         = desc,
                formatter_class     = RawTextHelpFormatter,
                add_help            = add_help
            )

    parserSelf.add_argument("--keyStore",
                    help    = "JSON formatted file containing read and write keys",
                    dest    = 'keyStore',
                    default = '')

    parserSelf.add_argument("--projectName",
                    help    = "The project name in the keyStore",
                    dest    = 'projectName',
                    default = '')

    parserSelf.add_argument("--readKey",
                    help    = "key to read from the purple air API",
                    dest    = 'readKey',
                    default = '')

    parserSelf.add_argument("--writeKey",
                    help    = "key to write to the purple air API",
                    dest    = 'writeKey',
                    default = '')

    parserSelf.add_argument("--sensorDataGet",
                    help    = "get data for the passed sensor ID",
                    dest    = 'sensorDataGet',
                    default = '')

    parserSelf.add_argument("--fields",
                    help    = "for a specific sensor, only retrieve the fields (comma separated list)",
                    dest    = 'fields',
                    default = '')

    parserSelf.add_argument("--fieldsList",
                    help    = "list the supported field keys",
                    dest    = 'fieldsList',
                    default = False,
                    action  = 'store_true')

    parserSelf.add_argument("--sensorsAddFromFile",
                    help    = "read sensor IDs from passed file and add to group",
                    dest    = 'sensorsAddFromFile',
                    default = '')

    parserSelf.add_argument("--sensorAddToGroup",
                    help    = "add a single sensor ID to a group",
                    dest    = 'sensorAddToGroup',
                    default = '')

    parserSelf.add_argument("--sensorsInGroupList",
                    help    = "list sensor IDs in --usingGroupID <group>",
                    dest    = 'sensorsInGroupList',
                    default = False,
                    action  = 'store_true')

    parserSelf.add_argument("--usingGroupID",
                    help    = "use the passed groupID",
                    dest    = 'usingGroupID',
                    default = '')

    parserSelf.add_argument("--sensorRefType",
                    help    = "sensor reference type: sensor_index | sensor_id",
                    dest    = 'sensorRefType',
                    default = 'sensor_index')

    parserSelf.add_argument("--asHistory",
                    help    = "if specified, do a history retrieve",
                    dest    = 'asHistory',
                    default = False,
                    action  = 'store_true')

    parserSelf.add_argument("--asHistoryCSV",
                    help    = "if specified, do a history retrieve as CSV",
                    dest    = 'asHistoryCSV',
                    default = False,
                    action  = 'store_true')

    parserSelf.add_argument("--start_timestamp",
                    help    = "a start timestamp in '%Y-%m-%d' format (for history calls)",
                    dest    = 'startTimestamp',
                    default = '')

    parserSelf.add_argument("--end_timestamp",
                    help    = "an end timestamp in '%Y-%m-%d' format (for history calls)",
                    dest    = 'endTimestamp',
                    default = '')

    parserSelf.add_argument("--version",
                    help    = "print name and version",
                    dest    = 'b_version',
                    default = False,
                    action  = 'store_true')

    parserSelf.add_argument("--man",
                    help    = "print man page",
                    dest    = 'man',
                    default = False,
                    action  = 'store_true')

    return parserSelf

def parser_interpret(parser, *args):
    """
    Interpret the list space of *args, or sys.argv[1:] if
    *args is empty
    """
    if len(args):
        args    = parser.parse_args(*args)
    else:
        args    = parser.parse_args(sys.argv[1:])
    return args

def parser_JSONinterpret(parser, d_JSONargs):
    """
    Interpret a JSON dictionary in lieu of CLI.

    For each <key>:<value> in the d_JSONargs, append to
    list two strings ["--<key>", "<value>"] and then
    argparse.
    """
    l_args  = []
    for k, v in d_JSONargs.items():
        if type(v) == type(True):
            if v: l_args.append('--%s' % k)
            continue
        l_args.append('--%s' % k)
        l_args.append('%s' % v)
    return parser_interpret(parser, l_args)

def date_toUNIX(str_date:str) -> int:
    ret:int     = 0
    try:
        date_obj:datetime.datetime  = datetime.datetime.strptime(str_date, "%Y-%m-%d")
        ret                         = int(date_obj.timestamp())
    except:
        pass
    return ret

class Persair:
    """

    A class that provides a python API for the purpleair API and
    that uses a local monogodb for data storage.

    """

    def  __init__(self, args, **kwargs) -> None:

        self.args:Namespace                 = Namespace()
        if type(args) is dict:
            parser:ArgumentParser           = parser_setup('Setup client using dict')
            options:Namespace               = parser_JSONinterpret(parser, args)
            self.args:Namespace             = options
        if type(args) is Namespace:
            self.args:Namespace             = args

        # get the read and write keys:
        d_APIaccess:dict            = self.readWrite_keysDefine()
        if not d_APIaccess['status']:
            self.exit_withMessage("Key define error!", 2, 'error')
        self.headersRead:dict       = {"X-API-Key": d_APIaccess['keys']['ReadKey']}
        self.headersWrite:dict      = {"X-API-Key": d_APIaccess['keys']['WriteKey']}

        # an aiohttp session
        self._session               = aiohttp.ClientSession()
        self.responseData:sensorModel.persairResponse   = sensorModel.persairResponse()

    def APIkeys_readFromFile(self) \
        -> dict[str, bool | str | dict[str, dict[Any, Any]]]:
        """
        Read a read/write key pair from a named <projectName> in
        the <keyStore> file (if it exists).

        Return
            dict[str, bool | dict[Any, Any]]: The Read/Write key pair with
                                              bool 'status'
        """
        d_keys:dict     =   {
            'status'        : False,
            'message'       : f'{self.args.keyStore} file not found.',
            'keys'          : {
                'ReadKey'   :   "",
                'WriteKey'  :   ""
            },
            'projectName'   : self.args.projectName
        }
        d_data:dict     = {}
        keyStore:Path   = Path(self.args.keyStore)
        if not keyStore.is_file():
            return d_keys
        with open(str(self.args.keyStore), 'r') as f:
            try:
                d_data:dict = json.load(f)
                if self.args.projectName in d_data:
                    d_data[self.args.projectName]['readwritekeys']  = \
                            self.args.projectName
                    d_keys['status']        = True
                    d_keys['keys']          = d_data[self.args.projectName]
                    d_keys['message']       = f'"{self.args.projectName}" loaded.'
                else:
                    d_keys['message']       = \
                        f'KeyStore does not have <projectName> {self.args.projectName}.'
            except:
                d_keys['message']           = \
                        f'Could not interpret key file {self.args.keyStore}.'
        return d_keys

    def readWrite_keysDefine(self) -> dict:
        d_APIaccess:dict  = {
                'status'    : False,
                'keys'      : {
                    'ReadKey'   : "",
                    'WriteKey'  : ""
                }
        }
        if self.args.keyStore and self.args.projectName:
            d_APIaccess = self.APIkeys_readFromFile()
        if self.args.readKey:
            d_APIaccess['keys']['ReadKey']  = self.args.readKey
        if self.args.writeKey:
            d_APIaccess['keys']['WriteKey'] = self.args.readKey
        if settings.keys.ReadKey:
            d_APIaccess['keys']['ReadKey']  = settings.keys.ReadKey
        if settings.keys.WriteKey:
            d_APIaccess['keys']['WriteKey'] = settings.keys.WriteKey

        if d_APIaccess['keys']['ReadKey'] and d_APIaccess['keys']['WriteKey']:
            d_APIaccess['status']           = True
        return d_APIaccess

    def exit_withMessage(self, message:str, code:int = 0, exitType:str = 'error') -> None:
        header:str  = ""
        match(exitType):
            case 'error':
                header  = f"{C.RED}ERROR!{C.NO_COLOUR}"
        print(header)
        print(message)
        sys.exit(code)

    def sensorFields_print(self):
        str_fieldInfo:str           =  f"""

        The 'Fields' parameter specifies which 'sensor data fields' to include in the response.
        It is a comma separated list with one or more of the following:

        {C.CYAN}Station information and status fields:{C.NO_COLOUR}
        name,             private,           firmware_version,     firmware_upgrade,
        icon,             model,             hardware,             led_brightness
        location_type,    altitude           latitude,             longitude,
        position_rating,  rssi,              pa_latency,           memory,
        uptime,           last_seen,         last_modified,        date_created,
        channel_state,    channel_flags,     channel_flags_manual, channel_flags_auto,
        confidence,       confidence_manual, confidence_auto

        {C.CYAN}Environmental fields:{C.NO_COLOUR}
        humidity,    humidity_a,    humidity_b,
        temperature, temperature_a, temperature_b,
        pressure,    pressure_a,    pressure_b

        {C.CYAN}Miscellaneous fields:{C.NO_COLOUR}
        voc, voc_a, voc_b, ozone1, analog_input

        {C.CYAN}PM1.0 fields:{C.NO_COLOUR}
        pm1.0,      pm1.0_a,      pm1.0_b,
        pm1.0_atm,  pm1.0_atm_a,  pm1.0_atm_b,
        pm1.0_cf_1, pm1.0_cf_1_a, pm1.0_cf_1_b

        {C.CYAN}PM2.5 fields:{C.NO_COLOUR}
        pm2.5_alt,  pm2.5_alt_a,  pm2.5_alt_b,
        pm2.5,      pm2.5_a,      pm2.5_b,
        pm2.5_atm,  pm2.5_atm_a,  pm2.5_atm_b,
        pm2.5_cf_1, pm2.5_cf_1_a, pm2.5_cf_1_b

        {C.CYAN}PM2.5 pseudo (simple running) average fields:{C.NO_COLOUR}
        pm2.5_10minute, pm2.5_10minute_a, pm2.5_10minute_b,
        pm2.5_30minute, pm2.5_30minute_a, pm2.5_30minute_b,
        pm2.5_60minute, pm2.5_60minute_a, pm2.5_60minute_b,
        pm2.5_6hour,    pm2.5_6hour_a,    pm2.5_6hour_b,
        pm2.5_24hour,   pm2.5_24hour_a,   pm2.5_24hour_b,
        pm2.5_1week,    pm2.5_1week_a,    pm2.5_1week_b

        {C.CYAN}PM10.0 fields:{C.NO_COLOUR}
        pm10.0,      pm10.0_a,      pm10.0_b,
        pm10.0_atm,  pm10.0_atm_a,  pm10.0_atm_b,
        pm10.0_cf_1, pm10.0_cf_1_a, pm10.0_cf_1_b

        {C.CYAN}Particle count fields:{C.NO_COLOUR}
         0.3_um_count,  0.3_um_count_a,  0.3_um_count_b,
         0.5_um_count,  0.5_um_count_a,  0.5_um_count_b,
         1.0_um_count,  1.0_um_count_a,  1.0_um_count_b,
         2.5_um_count,  2.5_um_count_a,  2.5_um_count_b,
         5.0_um_count,  5.0_um_count_a,  5.0_um_count_b,
        10.0_um_count, 10.0_um_count_a, 10.0_um_count_b

        {C.CYAN}ThingSpeak fields, used to retrieve data from
        api.thingspeak.com:{C.NO_COLOUR}
          primary_id_a,   primary_key_a,
        secondary_id_a, secondary_key_a,
          primary_id_b,   primary_key_b,
        secondary_id_b, secondary_key_b

        See {C.PURPLE}https://api.purpleair.com/#api-sensors-get-sensor-data{C.NO_COLOUR}
        """

        return str_fieldInfo

    async def purpleAir_call(
        self,
        url:str,
        auth:dict,
        **kwargs
    ) -> sensorModel.persairResponse:

        success_message:str     = 'success'
        failure_message:str     = 'failure'
        success_response:int    = 200
        body:dict               = {}
        verb:str                = "get"
        for k,v in kwargs.items():
            if k == 'success_message':  success_message     = v
            if k == 'failure_message':  failure_message     = v
            if k == 'success_response': success_response    = v
            if k == 'body':             body                = v
            if k == 'verb':             verb                = v

        d_ret:sensorModel.persairResponse   = sensorModel.persairResponse()
        match verb.lower():
            case 'get':
                response:ClientResponse = \
                    await self._session.get(url, headers = auth)
            case 'post':
                response:ClientResponse = \
                    await self._session.post(url, headers = auth, data = body)
            case _:
                response:ClientResponse = \
                    await self._session.get(url, headers = auth)
        try:
            d_resp:dict             = await response.json()
        except:
            d_resp:dict             = {"text": await response.text()}

        d_ret.response          = d_resp
        if response.status == success_response:
            d_ret.status        = True
            d_ret.message       = success_message
        else:
            d_ret.message       = f"{failure_message}: {response.status}"
        return d_ret

    async def sensor_dataGet(self, refsensor:str, fields:str="", history:str="") \
    -> sensorModel.persairResponse:

        def history_formulateQuery(history) -> str:
            str_historyQuery:str     = ""
            if not len(history):
                return ""
            if date_toUNIX(self.args.startTimestamp):
                str_historyQuery    += f"start_timestamp={date_toUNIX(self.args.startTimestamp)}&"
            if date_toUNIX(self.args.endTimestamp):
                str_historyQuery    += f"end_timestamp={date_toUNIX(self.args.endTimestamp)}&"
            return str_historyQuery

        def fields_formulateQuery(fields) -> str:
            str_fields:str  = ""
            if len(fields):
                str_fields  = f"fields={fields}"
            return str_fields

        # pudb.set_trace()
        str_url:str         = f"https://api.purpleair.com/v1/sensors/{refsensor}"
        str_query:str       = "?" if len(fields) + len(history) else ""
        str_query          += history_formulateQuery(history) + fields_formulateQuery(fields)
        str_url            += history + str_query

        d_ret:sensorModel.persairResponse   = sensorModel.persairResponse()
        d_ret               = await self.purpleAir_call(
                                str_url,
                                self.headersRead,
                                success_response = 200,
                                failure_message  = f"Error getting data for sensor <{refsensor}>")
        return d_ret

    def groupID_check(self, groupid)\
    -> tuple[sensorModel.persairResponse, bool]:
        b_OK    = True
        d_ret:sensorModel.persairResponse   = sensorModel.persairResponse()
        if not groupid:
            d_ret.message    = "No groupID specified. From CLI, use '--usingGroupID <groupid>'"
            b_OK             = False
        else:
            d_ret.message   = f"groupID {groupid} OK"
        return d_ret, b_OK

    async def sensor_toGroupAdd(self, refsensor:int, groupid:int) \
    -> sensorModel.persairResponse:
        # pudb.set_trace()
        d_ret:sensorModel.persairResponse   = sensorModel.persairResponse()
        OK:bool                             = False
        (d_ret, OK) = self.groupID_check(groupid)
        if not OK: return d_ret

        d_ret           = await self.purpleAir_call(
                            f"https://api.purpleair.com/v1/groups/{groupid}/members",
                            self.headersWrite,
                            body             = {
                                self.args.sensorRefType: refsensor
                            },
                            verb             = 'post',
                            success_response = 201,
                            failure_message  = f"Error adding sensor <{refsensor}> to group <{groupid}>")
        return d_ret

    async def sensors_toGroupFromFile(self, groupid:int, filename:Path) \
    -> sensorModel.persairResponse:
        d_ret:sensorModel.persairResponse   = sensorModel.persairResponse()
        OK:bool                             = False
        if not filename.is_file():
            d_ret.message = f"Sensor file '{filename}' is not accessible."
            return d_ret
        (d_ret, OK) = self.groupID_check(groupid)
        if not OK: return d_ret

        ld_additionResponse:list            = []
        with open(str(filename), 'r') as f:
            d_ret.status        = True
            summary:str         = ''
            for refsensor in f:
                refsensor:str = refsensor.strip()
                try:
                    irefsensor:int     = int(refsensor)
                    d_sensorAddition:sensorModel.persairResponse = \
                        await self.sensor_toGroupAdd(irefsensor, groupid)
                    ld_additionResponse.append(d_sensorAddition)
                except:
                    ld_additionResponse.append({
                        'error': f'Invalid refsensor {refsensor}'
                    })
                summary += f" {refsensor} "
            d_ret.message = summary
            d_ret.response = {"sensorAddition": ld_additionResponse}
        return d_ret

    async def sensors_inGroupGet(self, groupid:int) \
    -> sensorModel.persairResponse:
        d_ret:sensorModel.persairResponse   = sensorModel.persairResponse()
        OK:bool                             = False
        (d_ret, OK)     = self.groupID_check(groupid)
        if not OK: return d_ret
        d_ret           = await self.purpleAir_call(
                            f"https://api.purpleair.com/v1/groups/{groupid}",
                            self.headersRead,
                            failure_message = f"Error getting sensors in group {groupid}")
        return d_ret

    async def close(self) -> None:
        await self._session.close()

    async def service(self) -> None:
        # pudb.set_trace()

        if self.args.fieldsList:
            print(self.sensorFields_print())
            self.exit_withMessage("Returning to system", 0, 'info')

        d_data:sensorModel.persairResponse  = sensorModel.persairResponse()

        if self.args.sensorDataGet:
            str_history:str     = ""
            if self.args.asHistory:
                str_history     = f"/history"
            if self.args.asHistoryCSV:
                str_history     = f"/history/csv"
            d_data  = await self.sensor_dataGet(
                self.args.sensorDataGet,
                self.args.fields,
                str_history
            )
        if self.args.sensorAddToGroup:
            d_data  = await self.sensor_toGroupAdd(
                self.args.sensorAddToGroup, self.args.usingGroupID
            )
        if self.args.sensorsAddFromFile:
            d_data  = await self.sensors_toGroupFromFile(
                self.args.usingGroupID, Path(self.args.sensorsAddFromFile)
            )
        if self.args.sensorsInGroupList:
            d_data  = await self.sensors_inGroupGet(
                self.args.usingGroupID
            )

        # Close this comms session
        await self.close()
        self.responseData   = d_data

