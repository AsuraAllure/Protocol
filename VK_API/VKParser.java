package org.example;
public class VKParser {

    private boolean isDigit(char c) {
        return switch (c) {
            case '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' -> true;
            default -> false;
        };
    }

    private String find(String data, String s){
        int a = data.indexOf(s) + s.length() + 2;
        StringBuilder count = new StringBuilder();
        while ((data.charAt(a + 1) != '"')) {
            count.append(data.charAt(a + 1));
            a += 1;
        }
        if (count.length() == 0) {
            count.append('-');
        }
        return count.toString();
    }
    public String selectCountChats(String data) {
        int a = data.indexOf("messages") + "messages".length() + 1;
        StringBuilder count = new StringBuilder();
        while (isDigit(data.charAt(a + 1))) {

            count.append(data.charAt(a + 1));
            a += 1;
        }
        if (count.length() == 0) {
            count.append('0');
        }
        return count.toString();
    }

    public String selectCountry(String data){

        return find(data, "country");
    }
    public String selectProfileInfo(String data){
        return find(data, "first_name") + " " + find(data, "last_name");
    }
}



