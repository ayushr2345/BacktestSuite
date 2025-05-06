//#include <iostream>
//#include <Python.h>
//#include <filesystem>
//#include "Backtester.h"
//#include "LogMacros.h"
//
//int main(int argc, char* argv[])
//{
//    if (argc < 4)
//    {
//        LOG_ERROR("Insufficient arguments provided. Expected 4 arguments.");
//        std::cerr << "Usage: backtester <symbol> <timeframe> <start_date> <end_date>" << std::endl;
//        return 1;
//    }
//
//    std::string symbol = argv[1];
//    std::string timeFrame = argv[2];
//    std::string startDate = argv[3];
//    std::string endDate = argv[4];
//
//    LOG_DEBUG("Symbol: {}", symbol);
//    LOG_DEBUG("Time Frame: {}", timeFrame);
//    LOG_DEBUG("Start Date: {}", startDate);
//    LOG_DEBUG("End Date: {}", endDate);
//
//    logger::Logger::getInstance().setLogFile("backtester.log");
//    LOG_DEBUG("Backtester started");
//
//    // **Locate Virtual Environment**
//    std::filesystem::path venvPath = "G:\source\BacktestSuite\DataDownloader\DataDownloaderEnv";
//    std::filesystem::path venvPythonHome = venvPath / "Scripts"; // Windows venv structure
//
//    // **Configure Embedded Python**
//    LOG_DEBUG("Initializing Python Interpreter using venv...");
//
//    PyConfig config;
//    PyConfig_InitPythonConfig(&config);
//
//    // **Set Python home to the venv directory**
//    std::wstring venvHome = venvPythonHome.wstring();
//    config.home = const_cast<wchar_t*>((venvHome.c_str()));
//
//    // **Initialize Python**
//    Py_InitializeFromConfig(&config);
//    //PyConfig_Clear(&config);
//
//    // **Verify Interpreter Location**
//    PyRun_SimpleString("import sys; print('Python Interpreter:', sys.executable)");
//
//    // **Set Python Script Path**
//    PyRun_SimpleString("import sys");
//    std::string dataDownloaderPath = DATA_DOWNLOADER_PATH;
//
//#ifdef _WIN32
//    LOG_INFO("Windows Build System, replacing \\ with /");
//    std::replace(dataDownloaderPath.begin(), dataDownloaderPath.end(), '\\', '/');
//#endif
//
//    std::string pythonPathCmd = "sys.path.append('" + dataDownloaderPath + "')";
//    LOG_DEBUG("Python Path: {}", pythonPathCmd);
//    PyRun_SimpleString(pythonPathCmd.c_str());
//
//    // **Import Python Module & Call Function**
//    PyObject* pName = PyUnicode_DecodeFSDefault("DataDownloader");
//    PyObject* pModule = PyImport_Import(pName);
//    Py_DECREF(pName);
//
//
//    if (pModule != nullptr)
//    {
//        PyObject* pFunc = PyObject_GetAttrString(pModule, "download_data");
//
//        if (PyCallable_Check(pFunc))
//        {
//            PyObject* pArgs = PyTuple_New(4);
//            PyTuple_SetItem(pArgs, 0, PyUnicode_FromString(symbol.c_str()));  // example args
//            PyTuple_SetItem(pArgs, 1, PyUnicode_FromString(timeFrame.c_str()));
//            PyTuple_SetItem(pArgs, 2, PyUnicode_FromString(startDate.c_str()));
//            PyTuple_SetItem(pArgs, 3, PyUnicode_FromString(endDate.c_str()));
//
//            PyObject* pValue = PyObject_CallObject(pFunc, pArgs);
//            Py_DECREF(pArgs);
//
//            if (pValue != nullptr)
//            {
//                LOG_DEBUG("Python function returned successfully");
//                Py_DECREF(pValue);
//            }
//            else
//            {
//                PyErr_Print();
//                LOG_ERROR("Python function call failed");
//            }
//            Py_XDECREF(pFunc);
//        }
//        else
//        {
//            PyErr_Print();
//            LOG_ERROR("Python can't find function 'download_data'");
//        }
//        Py_DECREF(pModule);
//    }
//    else
//    {
//        PyErr_Print();
//        LOG_ERROR("Python failed to load 'DataDownloader' module");
//    }
//
//    Py_Finalize();
//    return 0;
//}

//#include <Python.h>
//#include <filesystem>
//#include "LogMacros.h"
//
//int main(int argc, char** argv)
//{
//    PyStatus status;
//
//    PyConfig config;
//
//
//    // **Locate Virtual Environment**
//    std::filesystem::path venvPath = "G:\source\BacktestSuite\DataDownloader\DataDownloaderEnv";
//    std::filesystem::path venvPythonHome = venvPath / "Scripts"; // Windows venv structure
//
//    // **Configure Embedded Python**
//    LOG_DEBUG("Initializing Python Interpreter using venv...");
//    // **Set Python home to the venv directory**
//    std::wstring venvHome = venvPythonHome.wstring();
//    config.home = const_cast<wchar_t*>((venvHome.c_str()));
//
//
//
//    PyConfig_InitPythonConfig(&config);
//    config.isolated = 0;
//
//    /* Decode command line arguments.
//       Implicitly preinitialize Python (in isolated mode). */
//    status = PyConfig_SetBytesArgv(&config, argc, argv);
//    if (PyStatus_Exception(status)) {
//        goto exception;
//    }
//
//    status = Py_InitializeFromConfig(&config);
//    if (PyStatus_Exception(status)) {
//        goto exception;
//    }
//    PyConfig_Clear(&config);
//
//    return Py_RunMain();
//
//exception:
//    PyConfig_Clear(&config);
//    if (PyStatus_IsExit(status)) {
//        return status.exitcode;
//    }
//    /* Display the error message and exit the process with
//       non-zero exit code */
//    Py_ExitStatusException(status);
//}




#include <Python.h>
#include <filesystem>
#include <iostream>

int main()
{
    PyStatus status;

    PyConfig config;
    PyConfig_InitPythonConfig(&config);

    /* Set the program name. Implicitly preinitialize Python. */
    status = PyConfig_SetString(&config, &config.program_name,
        L"G:/source/BacktestSuite/DataDownloader/DataDownloaderEnv/Scripts/python.exe");

    std::string venvSitePackages = "G:/source/BacktestSuite/DataDownloader/DataDownloaderEnv/Lib/site-packages";

    std::string pythonPathCmd = "import sys; sys.path.insert(0, '" + venvSitePackages + "')";
    if (PyStatus_Exception(status)) {
        goto exception;
    }

    status = PyConfig_SetString(&config, &config.executable,
        L"G:/source/BacktestSuite/DataDownloader/DataDownloaderEnv/Scripts/python.exe");

    if (PyStatus_Exception(status)) {
        goto exception;
    }


    status = Py_InitializeFromConfig(&config);
    if (PyStatus_Exception(status)) {
        goto exception;
    }
    PyConfig_Clear(&config);

    PyRun_SimpleString(pythonPathCmd.c_str());

    PyRun_SimpleString("import sys; print('Python sys.path:', sys.path)");
    PyRun_SimpleString("import pkgutil; print([module.name for module in pkgutil.iter_modules()])");


    PyRun_SimpleString("import os; import sys; print(sys.platlibdir)");
    PyRun_SimpleString("import pyotp; totp=pyotp.TOTP(''); print(totp.now())");
    PyRun_SimpleString("import pandas");
    return 0;

exception:
    PyConfig_Clear(&config);
    Py_ExitStatusException(status);
    return 0;
}