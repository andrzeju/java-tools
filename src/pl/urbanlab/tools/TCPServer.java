package pl.urbanlab.tools;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.net.ServerSocket;
import java.net.Socket;

public class TCPServer {

    public static void main(String[] args) {
        String clientWord;
        try {
            ServerSocket welcomeSocket = new ServerSocket(5555);
            Socket connectionSocket = welcomeSocket.accept();
            DataInputStream inFromClient =
                    new DataInputStream(connectionSocket.getInputStream());
            //create output stream, attached to socket
            DataOutputStream outToClient =
                    new DataOutputStream(connectionSocket.getOutputStream());
            //read in line from socket
            clientWord = inFromClient.readUTF();
            System.out.println(clientWord);
        } catch (Exception ex) {
            System.out.println("Ooops!");
            ex.printStackTrace();
        }
    }

}