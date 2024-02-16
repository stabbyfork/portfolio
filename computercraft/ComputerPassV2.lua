local version =2.216

--imports


--PASSWORDS
--password
local PASSWORD = ""
--ADMIN PASSWORD
local ADMIN_PASSWORD = ""

--vars
--if pass setup is ready
local passSetupReady = false
--if admin pass setup is ready
local adminSetupReady = false
--side to output redstone to
local redstoneSide = "left"
--admin status
local isAdmin = false
--obfuscation status
local obfuscationStatus = true
--are logins disabled
local isLocked = false

--key to obfuscate with, not saved in files yet
local obfuscationKey = "*"
--if loaded from file, don't put this in the save file
local loadedFromFile = false

-- normal commands
local CMDS = {
    {name="help", description="Lists all the commands available or details about the specified command", usage="help <command name>", args=1, optional=true},
    {name="<password>", description="Logs in with the correct password", usage="<password> <login duration (s)>", args=1, optional=true},
    {name="login_admin", description="Logs in with the correct admin password (and allows you to use admin commands)", usage="login_admin <admin_password>", args=1},
    {name="is_admin", description="Returns true/false if you are logged into administrator/or not", usage="is_admin <no args>", args=0},
    {name="clear", description="Clears the terminal", usage="clear <no args>", args=0},
}

-- ADMIN VARS AND WHATEVER
local ADMIN_CMDS = {
    {name="help_admin", description="Lists all the admin commands available or details about the specified command", usage="help_admin <admin command name> (optional)", args=1, optional=true},
    {name="reset", description="Resets the password", usage="reset <no args>", args=0},
    {name="login", description="Logs in for a specified duration, duration can be 'inf' to login forever", usage="login <duration (s or 'inf')>", args=1, optional=true},
    {name="logout_admin", description="Logs out of administrator", usage="logout_admin <no args>", args=0},
    {name="logout", description="Logs out of infinite logins", usage="logout <no args>", args=0},
    {name="reset_admin", description="Resets the administrator password", usage="reset_admin <no args>", args=0},
    {name="toggle_obf", description="Toggles text obfuscation ('*')", usage="toggle_obf <true/false>", args=1, optional=true},
    {name="redstone_side", description="Changes the side to output redstone power to", usage="redstone_side <side>", args=1, optional=true},
    {name="update", description="Checks for updates", usage="update <no args>", args=0},
    {name="lock", description="Locks/unlocks logins, use 'check' as an argument to check status", usage="lock <check>", args=1, optional=true},
}

--functions





--UTILITY
--writes text in color, args must be one letter or a built in color
local function writeColor (text, color, background)
    if color == nil then
        color = "5"
    elseif color == "green" then
        color = "d"
    elseif color == "orange" then
        color = "1"
    end
    if background == nil then
        background = "f"
    end
    local colorString = ""
    local colorList = {}
    local bgString = ""
    local bgList = {}
    for i = 1, string.len(text) do
        table.insert(colorList, color)
        table.insert(bgList, background)
    end
    colorString = table.concat(colorList, "")
    bgString = table.concat(bgList, "")
    term.blit(text, colorString, bgString)
end

--splits a string and returns a table
local function splitString (inputstr, sep)
        if sep == nil then
                sep = "%s"
        end
        local t={}
        for str in string.gmatch(inputstr, "([^"..sep.."]+)") do
                table.insert(t, str)
        end
        return t
end

--returns true if space is found
local function hasSpace(str)
    if str:match("%s") ~= nil then return true end
    return false
end

--string to boolean
local stringToBoolean={ ["true"]=true, ["false"]=false }

--read but obfuscated
local function readObf(obf)
    if obf == "" or obf == nil then
        return read()
    else
        return read(obf)
    end
end

--returns true in a table if string is one of value
local function hasString(...)
    local ret = {}
    for _,k in ipairs({...}) do ret[k] = true end
    return ret
end

--outputs redstone if not isLocked, doesn't output if isLocked
local function lockedLogin()
    if isLocked == true then
        printError("Locked")
        if isAdmin == true then writeColor("Use ", "orange") writeColor("lock") writeColor(" to unlock.", "orange") print() end
        return false
    else rs.setOutput(redstoneSide, true) return true end
end

--SAVE DATA TO FILE
local function saveToFile(file, ...)
    if fs.exists("/computerpass/saves") then
        fs.delete("/computerpass/saves")
    end
    file = "/computerpass/" .. file
    file = fs.open(file, "w")
    if arg.n == 0 then
        file.write("PASSWORD=" .. tostring(PASSWORD) .. ",") -- 1
        file.write("ADMIN_PASSWORD=" .. tostring(ADMIN_PASSWORD) .. ",") -- 2
        file.write("passSetupReady=" .. tostring(passSetupReady) .. ",") -- 3
        file.write("adminSetupReady=" .. tostring(adminSetupReady) .. ",") -- 4
        file.write("redstoneSide=" .. tostring(redstoneSide) .. ",") -- 5
        file.write("isAdmin=" .. tostring(isAdmin) .. ",") -- 6
        file.write("obfuscationStatus=" .. tostring(obfuscationStatus) .. ",") -- 7
        file.write("isLocked=" .. tostring(isLocked) .. ",") -- 8
    else
        for k, v in ipairs(arg) do
            file.write(tostring(arg[k].name) .. "=" .. tostring(arg[k].value) .. "\n")
        end
    end
    file.close()
end

-- CHECK ADMIN PWD
local function checkAdminPassword (adminPWD)
    if string.len(adminPWD) > 4 then
        if string.find(adminPWD,"%d") then
            if string.find(adminPWD, '%p') then
                writeColor("ADMINISTRATOR PASSWORD IS VALID. ENTER IT AGAIN.", "d") print()
                os.sleep(0.5)
                return true
            else
                printError("PASSWORD IS INVALID. IT MUST INCLUDE A SPECIAL CHARACTER.")
                os.sleep(1)
                return false
            end
        else
            printError("PASSWORD IS INVALID. IT MUST INCLUDE A DIGIT.")
            os.sleep(1)
            return false
        end
    else
        printError("PASSWORD IS INVALID. IT MUST CONSIST OF MORE THAN 5 CHARACTERS.")
        os.sleep(1)
        return false
    end
end

--CMDS
--if the input is in the command list
local function isInCmdList(inputList, inputStr)
    for k, v in ipairs(inputList) do
        if inputStr == inputList[k].name then
            return v
        end
    end
end

--help command
local function cmd_help(cmd)
    if cmd == nil then
        write("To learn more about a command, enter ") writeColor("help") print(" and the command name.")
        if isAdmin then writeColor("For admin commands, enter ", "orange") writeColor("help_admin") print(".") end
        for k, v in ipairs(CMDS) do
            write((v).name .. ", ")
        end
        print()
        return
    else
        for k, v in ipairs(CMDS) do
            if cmd == (v).name then
                write("Name: ") writeColor(textutils.serialise(CMDS[k].name)) print()
                print("Description: " .. tostring(textutils.serialise(CMDS[k].description)))
                write("Usage: ") writeColor(textutils.serialise(CMDS[k].usage)) print()
                if (v).args == 1 then
                    if (v).optional == nil then
                        print("Optional args: no")
                    elseif (v).optional == true then
                        print("Optional args: yes")
                    end
                end
                return
            end
        end
    end
    printError("No command for \"" .. tostring(cmd) .. "\".")
end


-- login to admin command
local function cmd_login_admin(pwd)
    if isAdmin then
        printError("YOU ARE ALREADY LOGGED INTO ADMINISTRATOR.")
        return
    elseif pwd == nil then
        print("ENTER THE ADMINISTRATOR PASSWORD.")
        if readObf(obfuscationKey) ~= ADMIN_PASSWORD then
            printError("INCORRECT PASSWORD.")
            return
        end
    elseif pwd ~= ADMIN_PASSWORD then
        printError("INCORRECT PASSWORD.")
        return
    end
    writeColor("PASSWORD IS CORRECT. LOGGING INTO ADMINISTRATOR...", "green") print()
    write("ENTER ") writeColor("help_admin") print(" FOR A LIST OF ADMIN COMMANDS.")
    isAdmin = true
    saveToFile("saves")
    os.sleep(1)
end

-- true if isAdmin
local function cmd_is_admin()
    if isAdmin == true then
        writeColor("true", "green") print()
    else
        printError("false")
    end
end

--clears the terminal
local function cmd_clear()
    term.clear()
    term.setCursorPos(1,1)
end



--ADMIN CMDS

-- logs out of admin
local function adm_logout_admin()
    printError("LOGGING OUT OF ADMINISTRATOR...")
    os.sleep(0.5)
    isAdmin = false
    saveToFile("saves")
end

-- admin cmd help
local function adm_help(cmd)
    if cmd == nil then
        write("To learn more about a command, enter ") writeColor("help_admin") print(" and the command name.")
        writeColor("ADMIN COMMANDS: ", "orange") print()
        for k, v in ipairs(ADMIN_CMDS) do
            write((v).name .. ", ")
        end
        print()
        return
    else
        for k, v in ipairs(ADMIN_CMDS) do
            if cmd == (v).name then
                write("Name: ") writeColor(textutils.serialise(ADMIN_CMDS[k].name)) print()
                print("Description: " .. tostring(textutils.serialise(ADMIN_CMDS[k].description)))
                write("Usage: ") writeColor(textutils.serialise(ADMIN_CMDS[k].usage)) print()
                if (v).args == 1 then
                    if (v).optional == nil then
                        print("Optional args: no")
                    elseif (v).optional == true then
                        print("Optional args: yes")
                    end
                end
                return
            end
        end
    end
    printError("No command for \"" .. tostring(cmd) .. "\".")
end

--resets admin password
local function adm_reset()
    print("ENTER THE PREVIOUS ADMINISTRATOR PASSWORD.")
    write("IF YOU WISH TO ABORT THE PROCESS, ENTER ") writeColor("exit") print(".")
    local adminPWD = readObf(obfuscationKey)
    if adminPWD == ADMIN_PASSWORD then
        writeColor("ADMINISTRATOR PASSWORDS MATCH.", "green") print()
        print("ENTER THE NEW ADMINISTRATOR PASSWORD. IT MUST: ") 
        writeColor("BE AT LEAST 5 CHARACTERS LONG", "1") print(";")
        writeColor("INCLUDE NUMBERS", "1") print(";")
        writeColor("INCLUDE SPECIAL CHARACTERS", "1") print(".")
        write("IF YOU WISH TO ABORT THE PROCESS, ENTER ") writeColor("exit") print(".")
        adminPWD = readObf(obfuscationKey)
        if hasSpace(adminPWD) then
            printError("ADMINISTRATOR PASSWORD MUST NOT CONTAIN SPACES.")
            os.sleep(0.5)
            return
        else
            if isInCmdList(CMDS, adminPWD) ~= nil then
                printError("ADMINISTRATOR PASSWORD MUST NOT MATCH BUILT-IN COMMANDS.")
                os.sleep(0.5)
                return
            else
                if isInCmdList(ADMIN_CMDS, adminPWD) ~= nil then
                    printError("ADMINISTRATOR PASSWORD MUST NOT MATCH BUILT-IN COMMANDS.")
                    os.sleep(0.5)
                    return
                else
                    if string.lower(adminPWD) == "exit" then
                        if adminSetupReady == false then printError("YOU MUST ESTABLISH AN ADMINISTRATOR PASSWORD FIRST.") os.sleep(2) term.clear() term.setCursorPos(1,1) else print("EXITING...") return end
                    else
                        if checkAdminPassword(adminPWD) then
                            local tempPwd = readObf(obfuscationKey)
                            if tempPwd == adminPWD then
                                writeColor("ADMINISTRATOR PASSWORD SUCCESSFULLY ESTABLISHED.", "d")
                                ADMIN_PASSWORD = adminPWD
                                adminSetupReady = true
                                saveToFile("saves")
                                os.sleep(2)
                                term.clear()
                                term.setCursorPos(1,1)
                                return
                            else
                                printError("PASSWORDS DO NOT MATCH.")
                                os.sleep(0.5)
                                return
                            end
                        end
                    end
                end
            end
        end
    elseif adminPWD == "exit" then
        print("EXITING...") return
    else
        printError("PASSWORDS DO NOT MATCH.")
        os.sleep(0.5)
        return
    end
end

--logs in for a duration
local function adm_login(dur)
    if dur == nil then
        dur = 5
    elseif dur == "inf" then
        write("Logged in for infinite time, ") writeColor("use ", "orange") writeColor("logout") writeColor(" to log out", "orange") print(".")
        lockedLogin()
        return
    end
    if tonumber(dur) then
        if lockedLogin() then
            writeColor("Logged in for " .. tostring(dur) .. " seconds.", "green") print()
            os.sleep(tonumber(dur))
            rs.setOutput(redstoneSide, false)
        end
    else
        printError("Duration is not a number!")
    end
end
--log out of infinite logins
local function adm_logout()
    if rs.getOutput(redstoneSide) then
        rs.setOutput(redstoneSide, false)
        print("Logged out")
    else
        printError("There is no infinite login active.")
    end
end

--toggle text obfuscation
local function adm_toggle_obf(state)
    if state == nil then
        obfuscationStatus = not obfuscationStatus
    elseif state == "true" or state == "false" then
        obfuscationStatus = stringToBoolean[state]
    else
        printError("No action supplied by \"" .. state .. "\".")
        return
    end
    if obfuscationStatus == false then
        obfuscationKey = ""
    else
        obfuscationKey = "*"
    end
    writeColor("Obfuscation status toggled to " .. tostring(obfuscationStatus) .. ".", "green") print()
    saveToFile("saves")
end

--change redstone side
local function adm_redstone_side(side)
    if side == nil then
        print("Redstone output is currently on/at the " .. redstoneSide .. ".")
    elseif hasString("right","left","bottom","top","front","back")[side] then
        redstoneSide = side
        saveToFile("saves")
        writeColor("Redstone output set to " .. side .. ".", "green") print()
    else
        printError("No side matching \"" .. side .. "\".") os.sleep(0.5)
    end
end

--check for updates and update if found
local function adm_update()
    local urlPiece = "pastebin.com"
    local request = http.get("https://" .. urlPiece .. "/raw/994DnND7")
    local updVer = request.readLine()
    updVer = splitString(updVer, "=")[2]
    if tonumber(updVer) > version then
        writeColor("There is an update available!", "green") print()
        print("Would you like to update? (Y/N)")
        writeColor("The updater will overwrite '/startup'.", "orange") print()
        if string.lower(read()) == "y" then
            if isAdmin then
                writeColor("Initialising update procedure...", "green") print()
                request.close()
                os.sleep(1)
                shell.run("/computerpass/updater")
                return true
            else
                printError("You must be an administrator to update!")
                request.close()
                return false
            end
        else
            print("The system has not been updated.")
            request.close()
            return true
        end
    else
        writeColor("The system is up to date.", "green") print()
        print("System version: " .. updVer)
        request.close()
        return false
    end
end

--locks logins
local function adm_lock(fnc)
    if fnc == nil then
        isLocked = not isLocked
        writeColor("Locked status toggled to " .. tostring(isLocked), "green") print()
    elseif fnc == "check" then
        print("Locked: " .. tostring(isLocked))
    else
        printError("No actions supplied by \"" .. tostring(fnc) .. "\".")
    end
    saveToFile("saves")
end







--INPUT AND LOGIN

--logs in normally
local function login (t)
    if lockedLogin() then
        writeColor("Successfully logged in for " .. t .. " seconds", "d") print()
        os.sleep(t)
        redstone.setOutput(redstoneSide, false)
    end
end

--checks input for commands and logs in
local function checkInputAndLogin(Pwd)
    local pwdList = splitString(Pwd)
    if pwdList[1] == nil then
        printError("Cannot be empty")
        return true
    elseif pwdList[1] == PASSWORD then
        if table.getn(pwdList) == 1 then
            login(5)
        elseif table.getn(pwdList) > 2 then
            printError("More than one argument")
        else
            if tonumber(pwdList[2]) ~= nil  then
                if tonumber(pwdList[2]) == 69 or tonumber(pwdList[2]) > 69 then
                    printError("Cannot login for over 69 seconds")
                else
                login(tonumber(pwdList[2]))
                end
            else
                printError("Could not login for \"" .. pwdList[2] .. "\" seconds")
            end
        end
        return true


        -- OTHER COMMANDS
    elseif string.lower(pwdList[1]) == "reset" then
        if isAdmin then
            writeColor("Are you sure you want to reset the password? ", "e") print() -- LINE BELOW
            writeColor("Enter ", "1") writeColor("Y") writeColor(" or ", "1") writeColor("N") writeColor(" (yes, no).", "1") print()
            write("At any moment, enter ") writeColor("exit") print(" to exit.")
            os.sleep(0.5)
            if string.lower(read()) == "y" then
                write("Enter the previous password: ")
                Pwd = readObf(obfuscationKey)
                if Pwd == PASSWORD then
                    writeColor("Enter the new password:", "1")
                    Pwd = readObf(obfuscationKey)
                    if isInCmdList(CMDS, Pwd) ~= nil or isInCmdList(ADMIN_CMDS, Pwd) ~= nil then
                        printError("The password cannot match built-in commands!")
                    else
                        if hasSpace(Pwd) then
                            printError("The password cannot contain spaces!")
                            os.sleep(0.5)
                        elseif string.lower(Pwd) == "exit" then return true
                        else
                            PASSWORD = Pwd
                            saveToFile("saves")
                            writeColor("Password successfully changed", "d") print()
                            return true
                        end
                    end
                else
                    return false
                end
            end
        else
            printError("You must be an administrator to run this command!")
        end
            print("The password has not been changed.")
            return true
    elseif isInCmdList(CMDS, string.lower(pwdList[1])) ~= nil then
        local command = (isInCmdList(CMDS, string.lower(pwdList[1]))).name
        if command == "help" then if table.getn(pwdList) > 1 then cmd_help(string.lower(pwdList[2])) else cmd_help() end
        elseif command == "<password>" then printError("You need to enter the password!") writeColor((isInCmdList(CMDS, "<password>")).usage) print()
        elseif command == "login_admin" then if pwdList[2] ~= nil then cmd_login_admin(pwdList[2]) else cmd_login_admin() end
        elseif command == "is_admin" then cmd_is_admin()
        elseif command == "clear" then cmd_clear() end
        return true




        --ADMIN COMMAND EXECS
    elseif isInCmdList(ADMIN_CMDS, string.lower(pwdList[1])) ~= nil and isAdmin == true then
        local command = (isInCmdList(ADMIN_CMDS, string.lower(pwdList[1]))).name
        if command == "logout_admin" then adm_logout_admin()
        elseif command == "help_admin" then if pwdList[2] ~= nil then adm_help(pwdList[2]) else adm_help() end
        elseif command == "reset_admin" then adm_reset()
        --reset is above
        elseif command == "login" then if pwdList[2] ~= nil then adm_login(pwdList[2]) else adm_login() end
        elseif command == "logout" then adm_logout()
        elseif command == "toggle_obf" then if pwdList[2] ~= nil then adm_toggle_obf(pwdList[2]) else adm_toggle_obf() end
        elseif command == "redstoneside" then if pwdList[2] ~= nil then adm_redstone_side(pwdList[2]) else adm_redstone_side() end
        elseif command == "update" then adm_update()
        elseif command == "lock" then if pwdList[2] ~= nil then adm_lock(pwdList[2]) else adm_lock() end
        end
        return true


    elseif isInCmdList(ADMIN_CMDS, string.lower(pwdList[1])) ~= nil and isAdmin == false then
        printError("You must be an administrator to run this command!")
        return true
    else
        return false
    end
end





--LOAD FROM SAVE FILE
local loadFile = fs.open("/computerpass/saves", "r")
if loadFile == nil then
    print("nil")
else
    local loadContents = loadFile.readAll()
    loadContents = splitString(loadContents, ",")
    for k, v in ipairs(loadContents) do
        local out = splitString(v, "=")
        if k == 1 then PASSWORD = out[2]
        elseif k == 2 then ADMIN_PASSWORD = out[2]
        elseif k == 3 then passSetupReady = stringToBoolean[out[2]]
        elseif k == 4 then adminSetupReady = stringToBoolean[out[2]]
        elseif k == 5 then redstoneSide = out[2]
        elseif k == 6 then isAdmin = stringToBoolean[out[2]]
        elseif k == 7 then obfuscationStatus = stringToBoolean[out[2]]
        elseif k == 8 then isLocked = stringToBoolean[out[2]]
        end
    end
    loadFile.close()
    loadedFromFile = true
end

--general setup

if obfuscationStatus == false then
    obfuscationKey = ""
else
    obfuscationKey = "*"
end


--setup
if passSetupReady == false then term.clear() term.setCursorPos(1,1) print("Welcome to ComputerPass V2, the simple password script for ComputerCraft!\nYou are setting up the script for the first time.") end
while passSetupReady == false do
    print("Enter the new password!")
    local pwdSetup = readObf(obfuscationKey)
    if hasSpace(pwdSetup) then
        printError("The password cannot contain spaces!")
        os.sleep(0.5)
    else
        if pwdSetup == "" then
            printError("The password cannot be empty!")
            os.sleep(0.5)
        else
            if isInCmdList(CMDS, pwdSetup) ~= nil or isInCmdList(ADMIN_CMDS, pwdSetup) ~= nil then
                printError("The password cannot match built-in commands!")
            else
                write("Enter the password again. To restart the process, type ") writeColor("restart") print(".")
                local tempPwd = readObf(obfuscationKey)
                if pwdSetup == tempPwd then
                    PASSWORD = pwdSetup
                    writeColor("Password has been set! Enter ", "d") writeColor("help") writeColor(" for help.\n", "d")
                    passSetupReady = true
                    saveToFile("saves")
                    os.sleep(2)
                    term.clear()
                    term.setCursorPos(1,1)
                elseif tempPwd == "restart" then
                    print("Restarting password process...")
                    os.sleep(1)
                else
                    printError("Passwords do not match! Try again.")
                    os.sleep(1)
                end
            end
        end
    end
end




-- ADMIN SETUP

if adminSetupReady == false then printError("Admin password has not been set! Set it now.") end
while adminSetupReady == false do
    print("ENTER THE NEW ADMINISTRATOR PASSWORD. IT MUST: ") 
    writeColor("BE AT LEAST 5 CHARACTERS LONG", "1") print(";")
    writeColor("INCLUDE NUMBERS", "1") print(";")
    writeColor("INCLUDE SPECIAL CHARACTERS", "1") print(".")
    write("IF YOU WISH TO ABORT THE PROCESS, ENTER ") writeColor("exit") print(".")
    local adminPWD = readObf(obfuscationKey)
    if hasSpace(adminPWD) then
        printError("ADMINISTRATOR PASSWORD MUST NOT CONTAIN SPACES.")
        os.sleep(1)
    else
        if isInCmdList(CMDS, adminPWD) ~= nil then
            printError("ADMINISTRATOR PASSWORD MUST NOT MATCH BUILT-IN COMMANDS.")
        else
            if isInCmdList(ADMIN_CMDS, adminPWD) ~= nil then
                printError("ADMINISTRATOR PASSWORD MUST NOT MATCH BUILT-IN COMMANDS.")
            else
                if string.lower(adminPWD) == "exit" then
                    if adminSetupReady == false then printError("YOU MUST ESTABLISH AN ADMINISTRATOR PASSWORD FIRST.") os.sleep(2) term.clear() term.setCursorPos(1,1) else break end
                else
                    if checkAdminPassword(adminPWD) then
                        local tempPwd = readObf(obfuscationKey)
                        if tempPwd == adminPWD then
                            writeColor("ADMINISTRATOR PASSWORD SUCCESSFULLY ESTABLISHED.", "d")
                            ADMIN_PASSWORD = adminPWD
                            adminSetupReady = true
                            saveToFile("saves")
                            os.sleep(2)
                            term.clear()
                            term.setCursorPos(1,1)
                        else
                            printError("PASSWORDS DO NOT MATCH.")
                            os.sleep(0.5)
                        end
                    end
                end
            end
        end
    end
end

--TERMINATION AVOIDANCE
local function avoidance_Install(upd)
    if upd == true then
        print("Updating the ComputerPassV2 termination avoidance system...")
        if not fs.exists("/computerpass/avoidance") then
            printError("Avoidance system has not been found! Installing...")
        else
            fs.delete("/computerpass/avoidance")
        end
    else
        if fs.exists("/computerpass/avoidance") then
            local id = multishell.launch({shell = shell, multishell = multishell}, "/computerpass/avoidance")
            multishell.setTitle(id, "avoiding taxes")
            return
        end
    end
    if not fs.exists("/computerpass") then
        fs.makeDir("/computerpass")
    end
    local avoidanceFile = fs.open("/computerpass/avoidance", "w")
    avoidanceFile.writeLine("print(\"Termination avoidance system deployed\")")
    avoidanceFile.writeLine("while true do")
    avoidanceFile.writeLine("if multishell.getTitle(1) == \"shell\" then")
    avoidanceFile.writeLine("os.reboot()")
    avoidanceFile.writeLine("end")
    avoidanceFile.writeLine("if multishell.getFocus() ~= 1 then")
    avoidanceFile.writeLine("os.reboot()")
    avoidanceFile.writeLine("end")
    avoidanceFile.writeLine("os.sleep(0.05)")
    avoidanceFile.writeLine("end")
    avoidanceFile.close()
    local id = multishell.launch({shell = shell, multishell = multishell}, "/computerpass/avoidance")
    multishell.setTitle(id, "avoiding taxes")
end


--TERMINATION AVOIDANCE INSTALLER
avoidance_Install(true)

--UPDATER FILE
local function updater_Install(upd)
    if upd == true then
        print("Updating the ComputerPassV2 updater...")
        if not fs.exists("/computerpass/updater") then
            printError("Updater has not been found! Installing...")
        else
            fs.delete("/computerpass/updater")
        end
    else
        if fs.exists("/computerpass/updater") then
            return
        end
    end
    if not fs.exists("/computerpass") then
        fs.makeDir("/computerpass")
    end
    local waitFile = fs.open("/computerpass/updater", "w")
    waitFile.writeLine("print(\"This is the updater for ComputerPassV2. Wait until the process completes. Do not terminate or shutdown the computer\")")
    waitFile.writeLine("if fs.exists(\"/startup\") then")
    waitFile.writeLine("fs.delete(\"/startup\")")
    waitFile.writeLine("end")
    waitFile.writeLine("shell.run(\"pastebin get 994DnND7 startup\")")
    waitFile.writeLine("print(\"Update complete. Rebooting...\")")
    waitFile.writeLine("os.sleep(2)")
    waitFile.writeLine("os.reboot()")
    waitFile.close()
end
--INSTALL THE UPDATER
updater_Install(true)

-- MAIN!!!
term.clear()
term.setCursorPos(1,1)
print("ComputerPassV2")
print("by stabbyfork")
if loadedFromFile then writeColor("Previous data has been successfully loaded.", "green") print() end
if multishell.getTitle(1) ~= "startup" then
    printError("This program must be saved at '/startup' to work properly!") os.sleep(1)
    if fs.exists("/startup") then
        printError("There is a program at '/startup'.") os.sleep(0.5)
        print("By continuing, the program stored at that path will be moved to '/startup_dupe'.")
        writeColor("The process will take place in..", "orange") print()
        local i = 5
        while i > -1 do
            print(i)
            os.sleep(1)
            i = i - 1
        end
        fs.move("/startup", "/startup_dupe")
        print("Old '/startup' file has been moved to '/startup_dupe'.") os.sleep(0.5)
        print("Saving and updating ComputerPassV2 to '/startup'...") os.sleep(0.5)
        if not adm_update() then
            shell.run("pastebin get 994DnND7 startup")
        end
    else
        print("There is no file at '/startup'.") os.sleep(0.5)
        print("Saving and updating ComputerPassV2 to '/startup' in..") print()
        local i = 5
        while i > -1 do
            print(i)
            os.sleep(1)
            i = i - 1
        end
        print("Processing...") os.sleep(1)
        if not adm_update() then
            shell.run("pastebin get 994DnND7 startup")
        end
    end
else
    adm_update()
end

while true do
    write("Enter password: ")
        if checkInputAndLogin(readObf(obfuscationKey)) then
            -- login
            multishell.getFocus()
        else
            printError("Incorrect password")
        end
end


--MADE BY stabbyfork ON Discord AND MC
