package org.example;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;


public class VK {
    private final VKParser parser;
    // vk1.a.XhfGj4Md-ofeS2VIyYvFCvTGP8J9ZlYFrnScQtep0xeGWT4KmkHnrYaSYskWC4nrxkLTPZf-cHNj-w8IqV66lQvvFgtbrAgZNoDYxWtxh1WmFPQFNQgCoBaoNsiSEPwZycZdg-V4Rgo_CgBKu9zI6TCQoIm4W8zJtxI2gj-owK6pnxCcHU3Qunb9NDTSto5kQtOS_ETu448cx4bwabtrIw
    private String tokenNotifications;
    private String urlReq;

    public VK() {
        this.parser = new VKParser();
        String tokenPath = "C:\\Users\\Пользователь\\Desktop\\Предметы\\Протоколы Интернета\\Практики\\Tasks VKAPI\\Protocol\\src\\main\\java\\org\\example\\token.txt";
        try (BufferedReader reader = new BufferedReader(new FileReader(tokenPath))) {
            tokenNotifications = reader.readLine();
        } catch (IOException ignored) {
        }
    }

    private boolean checkToken() {
        // Некорректный адрес
        this.urlReq = "https://api.vk.com/method/account.getCounter"
                + "s?&access_token="
                + tokenNotifications + "&v=5.131";
        String data = getVkData(urlReq);
        if (!data.contains("error")) {
            return false;
        }
        return true;
    }

    private String getVkData(String urlReq) {
        StringBuilder urlString = new StringBuilder();
        try {
            URL url = new URL(urlReq);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            BufferedReader in = new BufferedReader(
                    new InputStreamReader(connection.getInputStream()));
            String current;

            while ((current = in.readLine()) != null) {
                urlString.append(current);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return urlString.toString();
    }

    public String getInfoAboutUser() {
        String info = "";

        info += "Count unseen chats: " +
                parser.selectCountChats(getVkData("https://api.vk.com/method/account.getCounters?&access_token=" + tokenNotifications + "&v=5.131"))
                + '\n';
        info += "User country: " +
                parser.selectCountry(getVkData("https://api.vk.com/method/account.getInfo?&access_token=" + tokenNotifications + "&v=5.131"))
                + '\n';
        info +="Name: "+ parser.selectProfileInfo(getVkData("https://api.vk.com/method/account.getProfileInfo?&access_token=" + tokenNotifications + "&v=5.131"))
                + '\n';

        return info;
    }

}
