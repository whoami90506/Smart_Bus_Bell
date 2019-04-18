package com.example.user.busdriver;

import android.content.Context;
import android.graphics.Color;
import android.graphics.drawable.Drawable;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.BaseAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import java.util.List;

/**
 * Created by user on 2017/7/21.
 */

public class ListAdapter extends BaseAdapter {
    private LayoutInflater myInflater;
    private List<ListData> stops;

    public ListAdapter(Context context, List<ListData> list){
        myInflater = LayoutInflater.from(context);
        stops = list;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        ViewHolder holder = null;
        if(convertView==null){
            convertView = myInflater.inflate(R.layout.stoplist_item, null);
            holder = new ViewHolder(
                    (TextView) convertView.findViewById(R.id.goBack_text),
                    (TextView) convertView.findViewById(R.id.CarNum_text),
                    (TextView) convertView.findViewById(R.id.Stop_Text),
                    (ImageView)convertView.findViewById(R.id.bell)
            );
            convertView.setTag(holder);
        }else{
            holder = (ViewHolder) convertView.getTag();
        }

        ListData temp = (ListData)getItem(position);

        if(temp.isGoback())holder.goBack.setText("回");
        else holder.goBack.setText("去");

        String bus = temp.getBus();
        if(bus.length() > 7){
            int idx = bus.indexOf("-");
            if(idx !=-1){
                if(idx <= (bus.length()-1)/2)idx++;
                String s = bus.substring(0, idx) + "\n" + bus.substring(idx, bus.length());
                bus = s;
            }
        }
        holder.car.setText(bus);

        if(temp.isRing()){
            holder.bell.setVisibility(View.VISIBLE);
            if(temp.isRing4())holder.bell.setImageDrawable(LineListActivity.pic[3]);
            else if(temp.isRing3())holder.bell.setImageDrawable(LineListActivity.pic[2]);
            else if(temp.isRing2())holder.bell.setImageDrawable(LineListActivity.pic[1]);
            else holder.bell.setImageDrawable(LineListActivity.pic[0]);
        } else holder.bell.setVisibility(View.INVISIBLE);


        String nameZh = temp.getStopName();
        int idx = nameZh.indexOf("(");
        if(idx !=-1){
            if(nameZh.length() <9)idx = -1;
            else if(idx >=8 || nameZh.length()-idx >9)idx = (nameZh.length())/2;
        }else{
            if(nameZh.length() >=8)idx = (nameZh.length())/2;
        }

        if(idx != -1){
            String s = nameZh.substring(0, idx) + "\n" + nameZh.substring(idx, nameZh.length());
            nameZh = s;
        }

        holder.name.setText(nameZh);
        if(temp.isHere())holder.name.setTextColor(Color.RED);
        else holder.name.setTextColor(Color.BLACK);

        return  convertView;
    }

    private class ViewHolder {
        TextView goBack;
        TextView car;
        TextView name;
        ImageView bell;
        public ViewHolder(TextView _goBack, TextView _car, TextView _name, ImageView _bell){
            goBack = _goBack;
            car = _car;
            name = _name;
            bell = _bell;
        }
    }

    @Override
    public int getCount() {
        return stops.size();
    }

    @Override
    public Object getItem(int arg0) {
        return stops.get(arg0);
    }

    @Override
    public long getItemId(int position) {
        return stops.indexOf(getItem(position));
    }
}
