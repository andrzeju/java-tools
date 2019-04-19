package pl.urbanlab.tools;

import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.Socket;

public class TCPClient {

    public static void main(String[] args) {
        String temp;
        String displayBytes;
        try {
            BufferedReader inFromUser = new BufferedReader(new InputStreamReader(System.in));
            Socket clientSocket = new Socket("localhost", 5555);
            DataOutputStream outToServer =
                    new DataOutputStream(clientSocket.getOutputStream());

            System.out.print("Command : ");

            DataInputStream inFromServer = new DataInputStream(clientSocket.getInputStream());
            temp = inFromUser.readLine();

            outToServer.writeUTF(temp);
            outToServer.flush();

            while ((displayBytes = inFromServer.readUTF()) != null) {
                System.out.print(displayBytes);
            }
        } catch (Exception ex) {
            System.out.println("Ooops!");
            ex.printStackTrace();
        }
    }
}