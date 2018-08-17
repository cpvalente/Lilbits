-- grandMA Lua Plugin
-- send TCP message
-- edited from jason@badgersan.com
-- This is tested with gma v3.3.4.3 and panasonic PTDZ110x 17.08.2018

-- Make sure there is no password set, encription not implemented here
-- a macro should create a variable called message
-- SetVar $message="test";
-- you can also specify IP and PORT (not required)
-- SetVar $send_ip="127.0.0.1"
-- SetVar $send_port="8000"
-- call the plugin after setting these
-- Plugin malink

local function warning()
  local version = gma.show.getvar('VERSION')
  if version:find('^3.3.') then
    return true
  else
    local funcName = debug.getinfo(1).source
    local txt = [[
      Plugin %s does not work on V3.2 and lower. V%s may not work properly with this plugin.
    ]]
    return gma.gui.confirm('WARNING!!',txt:format(funcName, version))
  end
end

-- the string will come from the macro that calls the script
-- either way here it goes

local OFF = "AVMT 30"
local ON = "AVMT 31"
local PJ_IP, PJ_PORT = "127.0.0.1", 4352

local internal_name    = select(1,...)
local visible_name     = select(2,...)

gma.echo('Plugin '..internal_name..' was loaded') -- you will see this message in the system monitor

function sendString()
    -- load libraries
    local socket = require("socket/socket")
    local sendTCP = assert(socket.tcp())

    -- aux setup
    sendTCP:settimeout(1)

    -- look for parameters
    gmaString = gma.show.getvar('MESSAGE')
    host = gma.show.getvar('SEND_IP')
    port = gma.show.getvar('SEND_PORT')

    -- double check
    if gmaString == nil then
      gmaString = "test"
    end
    if host == nil then
      host = PJ_IP
    end
    if port == nil then
      port = PJ_PORT
    end

    gma.echo (gmaString)
    gma.echo (host)
    gma.echo (port)

    -- send it
    sendTCP:connect(host, port)
    sendTCP:send(gmaString .. "\r")
    -- I was using this for PJLINK so had to add the \r
    -- could have been a variable

    local status, err
    while true do
      status, err = sendTCP:receive()
      if status == nil then break end
    end

    sendTCP:close()

    if err == "Socket is not connected" then
      gma.echo('*** TCP Connect Error  not connected- No response from '..host..':'..port..' ***')
      return
    elseif err == "timeout" then
      gma.echo('*** TCP Connect Error  timeout - No response from '..host..':'..port..' ***')
      gma.feedback('TCP Send Error')
      return
    end
    gma.echo('*** TCP Message "'..gmaString..'" sent to '..host..':'..port..' ***')
    gma.feedback('TCP Send : "'..gmaString..'"')
 end

return sendString
