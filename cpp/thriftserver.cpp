
#include <thread>

#include <boost/asio/io_service.hpp>
#include <boost/asio/signal_set.hpp>

#include <thrift/server/TThreadPoolServer.h>
#include <thrift/concurrency/ThreadManager.h>
#include <thrift/concurrency/PosixThreadFactory.h>

#include "processrequest.h"
#include "applicationinputhandler.h"

using namespace ::apache::thrift::concurrency;

void handler( const boost::system::error_code& error, int signal_number)
{
  
  if (!error)
  {
    std::cout << "Received Signal : No " 
              << signal_number << " "
              << error.message() << std::endl;
              
  }else{
    std::cout << "Received Signal " << signal_number << std::endl;
  }
}


int main(int argc, char** argv){
  
  boost::asio::io_service io_service;
  boost::asio::signal_set signals(io_service, SIGINT, SIGTERM);
  signals.async_wait(handler);
  
  //Declare here.. 
  int port = 9292;
  boost::shared_ptr<ApplicationInputHandler> handler; 
  boost::shared_ptr<TProcessor> processor;
  boost::shared_ptr<TServerTransport> serverTransport;
  boost::shared_ptr<TTransportFactory> transportFactory;
  boost::shared_ptr<TProtocolFactory> protocolFactory(new TBinaryProtocolFactory());
  
  ProcessRequest m_pRequest;
  
  try{
    //Initialize here..
    handler.reset(new ApplicationInputHandler(m_pRequest));
    processor.reset(new ApplicationProcessor(handler));
    serverTransport.reset(new TServerSocket(port));
    transportFactory.reset(new TBufferedTransportFactory());
    
    boost::shared_ptr<PosixThreadFactory> threadFactory(new PosixThreadFactory());
    boost::shared_ptr<ThreadManager> theThreadManager = ThreadManager::newSimpleThreadManager(2);

    theThreadManager->threadFactory(threadFactory);
    theThreadManager->start();
    
    //start the services
    boost::shared_ptr<TThreadPoolServer> server(new TThreadPoolServer(processor, serverTransport, transportFactory, protocolFactory, theThreadManager));
    boost::shared_ptr<Runnable> runnable(server);
    boost::shared_ptr<Thread> thread(threadFactory->newThread(runnable));
    
    std::cout << "Starting the server.. " << std::endl;
    thread->start();
  
    
    std::cout << "Starting IO handler service.. " << std::endl;
    
    io_service.run();

    //stop all services..
    server->stop();
  
  }catch(std::exception& e){
     std::cout  << "Unhandled exception reached the top of main:" 
                << e.what()
                << ", application will now exit!" << std::endl;
      return EXIT_FAILURE; 
    }
    

  return EXIT_SUCCESS;

}