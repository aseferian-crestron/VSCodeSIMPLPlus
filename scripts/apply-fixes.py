#!/usr/bin/env python3
"""Write corrected .usp test files for all known-fixable failures."""

import os, sys

SUITE = os.path.join(os.path.dirname(__file__), '..', 'test-suite')

def write(relpath, content):
    full = os.path.normpath(os.path.join(SUITE, relpath))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  fixed: {os.path.basename(full)}")

# ── Bit & Byte ────────────────────────────────────────────────────────────────
write("Bit_and_Byte_Functions/HighWord.usp", """\
#SYMBOL_NAME "Test_HighWord"
#DEFAULT_VOLATILE

FUNCTION Main()
{
    LONG_INTEGER x;
    INTEGER y;
    x = 0xAABBCCDD;
    y = HighWord(x);
    Print("The UpperMost 16 Bits of %08X are %04X\\n", x, y);
}
""")

write("Bit_and_Byte_Functions/LowWord.usp", """\
#SYMBOL_NAME "Test_LowWord"
#DEFAULT_VOLATILE

FUNCTION Main()
{
    LONG_INTEGER x;
    INTEGER y;
    x = 0xAABBCCDD;
    y = LowWord(x);
    Print("The LowerMost 16 Bits of %08X are %04X\\n", x, y);
}
""")

# ── Data Conversion ────────────────────────────────────────────────────────────
write("Data_Conversion_Functions/ItoA.usp", """\
#SYMBOL_NAME "Test_ItoA"
#DEFAULT_VOLATILE

STRING_OUTPUT Code$;
ANALOG_INPUT VALUE;

CHANGE VALUE
{
    Code$ = ITOA(VALUE);
    PRINT("Code$ = %s\\n", ITOA(VALUE));
}
""")

write("Data_Conversion_Functions/ItoHex.usp", """\
#SYMBOL_NAME "Test_ItoHex"
#DEFAULT_VOLATILE

STRING_OUTPUT Code$;
ANALOG_INPUT VALUE;

CHANGE VALUE
{
    Code$ = ITOHEX(VALUE);
    PRINT("Code$ = %s\\n", ITOHEX(VALUE));
}
""")

write("Data_Conversion_Functions/Chr.usp", """\
#SYMBOL_NAME "Test_Chr"
#DEFAULT_VOLATILE

STRING_OUTPUT Code$;
ANALOG_INPUT VALUE;

CHANGE VALUE
{
    STRING temp[10];
    Code$ = CHR(VALUE);
    temp = CHR(VALUE);
    PRINT("Code = %s\\n", temp);
}
""")

write("Data_Conversion_Functions/LtoA.usp", """\
#SYMBOL_NAME "Test_LtoA"
#DEFAULT_VOLATILE

STRING_OUTPUT Code$;

FUNCTION Main()
{
    LONG_INTEGER VALUE;
    STRING temp[50];
    VALUE = 1234567890;
    Code$ = LTOA(VALUE);
    temp = LTOA(VALUE);
    PRINT("Code = %s\\n", temp);
}
""")

write("Data_Conversion_Functions/LtoHex.usp", """\
#SYMBOL_NAME "Test_LtoHex"
#DEFAULT_VOLATILE

STRING_OUTPUT Code$;

FUNCTION Main()
{
    LONG_INTEGER VALUE;
    STRING temp[50];
    VALUE = 0xDEADBEEF;
    Code$ = LTOHEX(VALUE);
    temp = LTOHEX(VALUE);
    PRINT("Code = %s\\n", temp);
}
""")

write("Data_Conversion_Functions/HexToSI.usp", """\
#SYMBOL_NAME "Test_HexToSI"
#DEFAULT_VOLATILE

FUNCTION Main()
{
    SIGNED_INTEGER V1, V2;
    V1 = HexToSI("FFFF");
    V2 = HexToSI("AFFFB");
    PRINT("V1=%d, V2=%d\\n", V1, V2);
}
""")

# ── String Parsing ─────────────────────────────────────────────────────────────
write("String_Parsing_and_Manipulation_Functions/Right.usp", """\
#SYMBOL_NAME "Test_Right"
#DEFAULT_VOLATILE

STRING_INPUT Var$[100];
STRING Temp$[100];

CHANGE Var$
{
    Temp$ = RIGHT(Var$, 5);
    PRINT("Right most 5 chars of %s are %s\\n", Var$, Temp$);
}
""")

write("String_Parsing_and_Manipulation_Functions/Remove.usp", """\
#SYMBOL_NAME "Test_Remove"
#DEFAULT_VOLATILE

BUFFER_INPUT Source$[50];
STRING Output$[50];

CHANGE Source$
{
    Output$ = REMOVE("abc", Source$);
    PRINT("Remaining: %s\\n", Output$);
}
""")

write("String_Parsing_and_Manipulation_Functions/ResizeString.usp", """\
#SYMBOL_NAME "Test_ResizeString"
#DEFAULT_VOLATILE

DYNAMIC STRING MyString[10];

FUNCTION Main()
{
    SIGNED_INTEGER Status;
    Status = ResizeString(MyString, 200);
    IF (Status <> 0)
        Print("Error resizing MyString\\n");
}
""")

write("String_Parsing_and_Manipulation_Functions/CompareStrings.usp", """\
#SYMBOL_NAME "Test_CompareStrings"
#DEFAULT_VOLATILE

FUNCTION Main()
{
    STRING FirstString[100], SecondString[100];
    SIGNED_INTEGER result;
    FirstString = "ValueA";
    SecondString = "Valueb";
    result = CompareStrings(FirstString, SecondString);
    PRINT("CompareStrings result: %d\\n", result);
}
""")

write("String_Parsing_and_Manipulation_Functions/CompareStringsNoCase.usp", """\
#SYMBOL_NAME "Test_CompareStringsNoCase"
#DEFAULT_VOLATILE

FUNCTION Main()
{
    STRING FirstString[100], SecondString[100];
    SIGNED_INTEGER result;
    FirstString = "Valuea";
    SecondString = "Valueb";
    result = CompareStringsNoCase(FirstString, SecondString);
    PRINT("CompareStringsNoCase result: %d\\n", result);
}
""")

write("String_Parsing_and_Manipulation_Functions/ReverseFindNoCase.usp", """\
#SYMBOL_NAME "Test_ReverseFindNoCase"
#DEFAULT_VOLATILE

STRING_INPUT IN$[100];
INTEGER START_LOC;

CHANGE IN$
{
    START_LOC = ReverseFindNoCase("XYZ", IN$, 0);
    PRINT("Last XYZ at position %d in %s\\n", START_LOC, IN$);
}
""")

write("String_Parsing_and_Manipulation_Functions/ClearBuffer.usp", """\
#SYMBOL_NAME "Test_ClearBuffer"
#DEFAULT_VOLATILE

BUFFER_INPUT IN$[100];

CHANGE IN$
{
    IF (RIGHT(IN$, 1) = "Z")
        CLEARBUFFER(IN$);
    // Code to process IN$ goes here.
}
""")

write("String_Parsing_and_Manipulation_Functions/GatherByLength.usp", """\
#SYMBOL_NAME "Test_GatherByLength"
#DEFAULT_VOLATILE

#DEFINE_CONSTANT GATHER_TIMEOUT 200

BUFFER_INPUT MyLengthString[1000];

CHANGE MyLengthString
{
    STRING LocalString[256];
    WHILE (1)
    {
        LocalString = GatherByLength(20, MyLengthString, GATHER_TIMEOUT);
        IF (Len(LocalString) = 0)
        {
            ClearBuffer(MyLengthString);
            Print("Timeout in length string\\n");
            BREAK;
        }
        Print("Received %d bytes\\n", Len(LocalString));
    }
}
""")

# ── String Formatting ─────────────────────────────────────────────────────────
write("String_Formatting_and_Printing_Functions/Print.usp", """\
#SYMBOL_NAME "Test_Print"
#DEFAULT_VOLATILE

INTEGER X;
STRING Z[100];

FUNCTION MAIN()
{
    X = 10;
    Z = "Hello";
    PRINT("This is a string\\n");
    PRINT("Value of X is %u decimal, %02X hex\\n", X, X);
    PRINT("String value is %s\\n", Z);
}
""")

write("String_Formatting_and_Printing_Functions/MakeString.usp", """\
#SYMBOL_NAME "Test_MakeString"
#DEFAULT_VOLATILE

INTEGER X;
STRING Z[100], OUT[100];

FUNCTION MAIN()
{
    X = 10;
    Z = "Hello";
    MAKESTRING(OUT, "This is string\\n");
    MAKESTRING(OUT, "Value of X is %u decimal, %02X hex\\n", X, X);
    MAKESTRING(OUT, "String value is %s\\n", Z);
    PRINT("%s", OUT);
}
""")

write("String_Formatting_and_Printing_Functions/TRACE.usp", """\
#SYMBOL_NAME "Test_TRACE"
#DEFAULT_VOLATILE

FUNCTION Main()
{
    INTEGER x;
    x = 42;
    TRACE("Test value: %d\\n", x);
}
""")

# ── Mathematical ───────────────────────────────────────────────────────────────
write("Mathematical_Functions/Abs.usp", """\
#SYMBOL_NAME "Test_Abs"
#DEFAULT_VOLATILE

DIGITAL_INPUT TRIG;
INTEGER I, K;

CHANGE TRIG
{
    I = -5;
    K = ABS(I);
    PRINT("Original=%d  Absolute=%d\\n", I, K);
}
""")

write("Mathematical_Functions/MulDiv.usp", """\
#SYMBOL_NAME "Test_MulDiv"
#DEFAULT_VOLATILE

INTEGER X, Y;

FUNCTION MAIN()
{
    X = 1970;
    Y = 40;
    PRINT("(%d * %d)/25 = %d\\n", X, Y, MULDIV(X, Y, 25));
}
""")

# ── Random ────────────────────────────────────────────────────────────────────
write("Random_Number_Functions/Random.usp", """\
#SYMBOL_NAME "Test_Random"
#DEFAULT_VOLATILE

INTEGER NUM;

FUNCTION MAIN()
{
    NUM = RANDOM(25, 80);
    PRINT("Random between 25 and 80: %u\\n", NUM);
}
""")

# ── Array ─────────────────────────────────────────────────────────────────────
write("Array_Operations/ResizeArray.usp", """\
#SYMBOL_NAME "Test_ResizeArray"
#DEFAULT_VOLATILE

INTEGER MyIntArray[10][10];
STRING MyStringArray[10][10];

FUNCTION Main()
{
    SIGNED_INTEGER Status;
    Status = ResizeArray(MyStringArray, 200, 80);
    IF (Status <> 0)
        Print("Error resizing MyStringArray\\n");
    Status = ResizeArray(MyIntArray, 200, 100);
    IF (Status <> 0)
        Print("Error resizing MyIntArray\\n");
}
""")

write("Array_Operations/ResizeStructureArray.usp", """\
#SYMBOL_NAME "Test_ResizeStructureArray"
#DEFAULT_VOLATILE

STRUCTURE tagMyStruct
{
    INTEGER MyIntArray[10][10];
    STRING  MyStrArray[10][10];
}

DYNAMIC tagMyStruct myStructArr[10];

FUNCTION Main()
{
    SIGNED_INTEGER Status;
    Status = ResizeStructureArray(myStructArr, 20);
    IF (Status <> 0)
        Print("Error resizing myStructArr\\n");
}
""")

# ── File Functions ─────────────────────────────────────────────────────────────
write("File_Functions/FileOpen.usp", """\
#SYMBOL_NAME "Test_FileOpen"
#DEFAULT_VOLATILE

FUNCTION Main()
{
    SIGNED_INTEGER nFileHandle;
    StartFileOperations();
    nFileHandle = FileOpen("\\\\CF0\\\\MyFile", _O_RDONLY | _O_TEXT);
    IF (nFileHandle < 0)
        PRINT("Error opening MyFile\\n");
    ELSE
        FileClose(nFileHandle);
    EndFileOperations();
}
""")

write("File_Functions/FileOpenShared.usp", """\
#SYMBOL_NAME "Test_FileOpenShared"
#DEFAULT_VOLATILE

FUNCTION Main()
{
    SIGNED_INTEGER nFileHandle;
    StartFileOperations();
    nFileHandle = FileOpenShared("\\\\CF0\\\\MyFile", _O_RDONLY | _O_TEXT);
    IF (nFileHandle < 0)
        PRINT("Error opening MyFile\\n");
    ELSE
        FileClose(nFileHandle);
    EndFileOperations();
}
""")

write("File_Functions/FileSeek.usp", """\
#SYMBOL_NAME "Test_FileSeek"
#DEFAULT_VOLATILE

FUNCTION Main()
{
    SIGNED_INTEGER nFileHandle;
    StartFileOperations();
    nFileHandle = FileOpen("\\\\CF0\\\\MyFile", _O_RDONLY | _O_TEXT);
    IF (nFileHandle >= 0)
    {
        IF (FileSeek(nFileHandle, 0, SEEK_SET) < 0)
            PRINT("Error seeking file\\n");
        IF (FileClose(nFileHandle) <> 0)
            PRINT("Error closing file\\n");
    }
    EndFileOperations();
}
""")

write("File_Functions/WriteStructure.usp", """\
#SYMBOL_NAME "Test_WriteStructure"
#DEFAULT_VOLATILE

STRUCTURE PhoneBookEntry
{
    STRING Name[50];
    STRING Address[100];
    STRING PhoneNumber[20];
}

FUNCTION Main()
{
    SIGNED_INTEGER nFileHandle, nBytesWritten;
    PhoneBookEntry entry;
    entry.Name = "John Doe";
    entry.Address = "123 Main St";
    entry.PhoneNumber = "555-1234";
    StartFileOperations();
    nFileHandle = FileOpen("\\\\CF0\\\\phonebook.dat", _O_WRONLY | _O_CREAT | _O_TRUNC | _O_BINARY);
    IF (nFileHandle >= 0)
    {
        nBytesWritten = WriteStructure(nFileHandle, entry);
        FileClose(nFileHandle);
    }
    EndFileOperations();
}
""")

write("File_Functions/IsNull.usp", """\
#SYMBOL_NAME "Test_IsNull"
#DEFAULT_VOLATILE

STRUCTURE TestStruct
{
    INTEGER x;
}

FUNCTION Main()
{
    TestStruct s;
    INTEGER result;
    result = IsNull(s);
    PRINT("IsNull result: %d\\n", result);
}
""")

# ── Events ────────────────────────────────────────────────────────────────────
write("Events/THREADSAFE.usp", """\
#SYMBOL_NAME "Test_THREADSAFE"
#DEFAULT_VOLATILE

DIGITAL_INPUT DigInp;
INTEGER semaphore;

THREADSAFE PUSH DigInp
{
    IF (semaphore = 0)
    {
        semaphore = 1;
        Print("THREADSAFE handler entered\\n");
        semaphore = 0;
    }
}

FUNCTION Main()
{
    semaphore = 0;
}
""")

# ── Exception Handling ────────────────────────────────────────────────────────
write("Exception_Handling/GetExceptionMessage.usp", """\
#SYMBOL_NAME "Test_GetExceptionMessage"
#DEFAULT_VOLATILE

FUNCTION MyFunc(INTEGER index)
{
    INTEGER intArr[10];
    TRY
    {
        intArr[index] = 1;
        Print("Array index set\\n");
    }
    CATCH
    {
        Print("Exception: %s\\n", GetExceptionMessage());
    }
}

FUNCTION Main()
{
    MyFunc(11);
}
""")

# ── System Control ────────────────────────────────────────────────────────────
write("System_Control/WaitForInitializationComplete.usp", """\
#SYMBOL_NAME "Test_WaitForInitializationComplete"
#DEFAULT_VOLATILE

DIGITAL_INPUT diEnable;
INTEGER giProcessEnabled;

FUNCTION Main()
{
    giProcessEnabled = 0;
    IF (WaitForInitializationComplete() < 0)
    {
        Print("Error waiting for initialization\\n");
        RETURN;
    }
    Print("Initialization complete\\n");
    giProcessEnabled = 1;
}
""")

# ── System Interfacing ────────────────────────────────────────────────────────
write("System_Interfacing/GenerateUserError.usp", """\
#SYMBOL_NAME "Test_GenerateUserError"
#DEFAULT_VOLATILE

FUNCTION Main()
{
    STRING sError[100];
    sError = "Projector";
    GenerateUserError("The %s bulb has exceeded %d hours", sError, 1000);
}
""")

write("System_Interfacing/GenerateUserNotice.usp", """\
#SYMBOL_NAME "Test_GenerateUserNotice"
#DEFAULT_VOLATILE

FUNCTION Main()
{
    STRING sNotice[100];
    sNotice = "System";
    GenerateUserNotice("The %s started successfully", sNotice);
}
""")

write("System_Interfacing/GenerateUserWarning.usp", """\
#SYMBOL_NAME "Test_GenerateUserWarning"
#DEFAULT_VOLATILE

FUNCTION Main()
{
    STRING sWarning[100];
    sWarning = "Battery";
    GenerateUserWarning("The %s level is low", sWarning);
}
""")

# ── Time & Date ───────────────────────────────────────────────────────────────
write("Time_and_Date_Functions/GETHSECONDS.usp", """\
#SYMBOL_NAME "Test_GETHSECONDS"
#DEFAULT_VOLATILE

FUNCTION Main()
{
    INTEGER OldTime, NewTime, Loop;
    Loop = 0;
    OldTime = GETHSECONDS();
    WHILE (Loop < 10000)
    {
        Loop = Loop + 1;
    }
    NewTime = GETHSECONDS();
    PRINT("10000 iterations took %d hundredths of a second\\n", NewTime - OldTime);
}
""")

write("Time_and_Date_Functions/SETDATE.usp", """\
#SYMBOL_NAME "Test_SETDATE"
#DEFAULT_VOLATILE

ANALOG_INPUT MonthIn, DayIn, YearIn;

CHANGE MonthIn, DayIn, YearIn
{
    SetDate(MonthIn, DayIn, YearIn);
    PRINT("Date set: %s\\n", Date(1));
}
""")

# ── Compiler Directives ───────────────────────────────────────────────────────
write("Compiler_Directives/DEFAULT_NONVOLATILE.usp", """\
#SYMBOL_NAME "Test_DEFAULT_NONVOLATILE"
#DEFAULT_NONVOLATILE

DIGITAL_INPUT _SKIP_,Test_DIn;

PUSH Test_DIn
{
    Print("directive test\\n");
}
""")

# ── Socket ────────────────────────────────────────────────────────────────────
write("Direct_Socket_Access/SocketSend.usp", """\
#SYMBOL_NAME "Test_SocketSend"
#DEFAULT_VOLATILE

TCP_CLIENT MyTCPClient[1024];

FUNCTION Main()
{
    STRING msg[256];
    msg = "Hello\\n";
    SocketSend(MyTCPClient, msg);
}
""")

write("Direct_Socket_Access/SocketServerStartListen.usp", """\
#SYMBOL_NAME "Test_SocketServerStartListen"
#DEFAULT_VOLATILE

TCP_SERVER MyTCPServer[1024];

FUNCTION Main()
{
    SIGNED_INTEGER result;
    result = SocketServerStartListen(MyTCPServer, "", 41794);
    IF (result < 0)
        Print("Error starting listen: %d\\n", result);
}
""")

write("Direct_Socket_Access/SocketGetSenderIPAddress.usp", """\
#SYMBOL_NAME "Test_SocketGetSenderIPAddress"
#DEFAULT_VOLATILE

UDP_SOCKET MyUDPSocket[1024];

SOCKETRECEIVE MyUDPSocket
{
    STRING senderIP[50];
    SocketGetSenderIPAddress(MyUDPSocket, senderIP);
    Print("Received from: %s\\n", senderIP);
}
""")

# ── Ramping ───────────────────────────────────────────────────────────────────
write("Ramping_Functions/CreateRamp.usp", """\
#SYMBOL_NAME "Test_CreateRamp"
#DEFAULT_VOLATILE

DIGITAL_INPUT GoToPresetLevel;
ANALOG_OUTPUT LightLevel[20];

PUSH GoToPresetLevel
{
    RAMP_INFO LightInfo;
    SIGNED_INTEGER status;
    InitializeRampInfo(LightInfo);
    LightInfo.rampTargetValue = 6553;
    LightInfo.rampType = 1;
    LightInfo.rampTransitionTime = 1000;
    IF (IsSignalDefined(LightLevel[1]))
    {
        status = CreateRamp(LightLevel[1], LightInfo);
    }
}
""")

print(f"\nAll fixes applied to: {os.path.abspath(SUITE)}")
