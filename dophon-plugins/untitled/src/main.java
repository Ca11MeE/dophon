import sun.misc.BASE64Decoder;

import java.io.*;

public class main {

    public static void main(String args[]) throws IOException {
        File file = new File("F:\\person\\dophon\\dophon-plugins\\untitled\\src\\file_base_64");
        FileInputStream file_data = new FileInputStream(file);
        byte[] cache = new byte[(int) file.length()];
        StringBuilder base = new StringBuilder();
        int len = -1;
        while ((len = file_data.read(cache)) > -1) {
            base.append(new String(cache));
        }
        String cache_base = base.toString();
        System.out.println(cache_base);
        String path = "./demo.png";
        Base64ToImage(cache_base, path);
        //        if (base == null) {
//            System.out.println("字符串为空!");
//        }
    }

    public static boolean Base64ToImage_test(){
        base
    }


    /**
     * base64字符串转换成图片
     * @param imgStr		base64字符串
     * @param imgFilePath	图片存放路径
     * @return
     *
     * @author ZHANGJL
     * @dateTime 2018-02-23 14:42:17
     */
    public static boolean Base64ToImage(String imgStr,String imgFilePath) { // 对字节数组字符串进行Base64解码并生成图片

//        if (StringUtil.isEmpty(imgStr)) // 图像数据为空
//            return false;
        BASE64Decoder decoder = new BASE64Decoder();
        try {
            // Base64解码
            byte[] b = decoder.decodeBuffer(imgStr);
            for (int i = 0; i < b.length; ++i) {
                if (b[i] < 0) {
                    // 调整异常数据
                    b[i] += 256;
                }
            }

            OutputStream out = new FileOutputStream(imgFilePath);
            out.write(b);
            out.flush();
            out.close();

            return true;
        } catch (Exception e) {
            return false;
        }

    }

}