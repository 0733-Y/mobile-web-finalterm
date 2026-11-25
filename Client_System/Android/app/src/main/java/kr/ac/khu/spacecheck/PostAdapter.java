package kr.ac.khu.spacecheck;

import android.graphics.drawable.GradientDrawable;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import kr.ac.khu.spacecheck.model.Post;

/** Post 목록 한 줄: 썸네일, 제목, 인원·공간, 혼잡도 라벨(색), 시각. 3-1 */
public class PostAdapter extends RecyclerView.Adapter<PostAdapter.Holder> {

    public interface OnPostClick {
        void onClick(Post post);
    }

    private final List<Post> items = new ArrayList<>();
    private final Map<Integer, String> spaceNames = new HashMap<>();
    private final OnPostClick listener;

    public PostAdapter(OnPostClick listener) {
        this.listener = listener;
    }

    public void setSpaceNames(Map<Integer, String> names) {
        spaceNames.clear();
        spaceNames.putAll(names);
        notifyDataSetChanged();
    }

    public void replace(List<Post> posts) {
        items.clear();
        items.addAll(posts);
        notifyDataSetChanged();
    }

    public void append(List<Post> posts) {
        int start = items.size();
        items.addAll(posts);
        notifyItemRangeInserted(start, posts.size());
    }

    public Post first() {
        return items.isEmpty() ? null : items.get(0);
    }

    @NonNull
    @Override
    public Holder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_post, parent, false);
        return new Holder(v);
    }

    @Override
    public void onBindViewHolder(@NonNull Holder h, int position) {
        Post p = items.get(position);
        h.title.setText(p.title);
        String space = p.space == null ? h.itemView.getContext().getString(R.string.no_space)
                : spaceNames.getOrDefault(p.space, "#" + p.space);
        h.people.setText(h.itemView.getContext().getString(R.string.people_and_space, p.personCount, space));
        h.time.setText(TimeUtil.format(TimeUtil.parse(p.publishedDate)));
        bindLevel(h.level, p.level);
        ImageLoader.load(p.image, h.thumb);
        h.itemView.setOnClickListener(v -> listener.onClick(p));
    }

    static void bindLevel(TextView view, String level) {
        view.setText(LevelStyle.label(level));
        GradientDrawable bg = new GradientDrawable();
        bg.setCornerRadius(24f);
        bg.setColor(LevelStyle.color(level));
        view.setBackground(bg);
    }

    @Override
    public int getItemCount() {
        return items.size();
    }

    static class Holder extends RecyclerView.ViewHolder {
        final ImageView thumb;
        final TextView title;
        final TextView people;
        final TextView level;
        final TextView time;

        Holder(View v) {
            super(v);
            thumb = v.findViewById(R.id.post_thumb);
            title = v.findViewById(R.id.post_title);
            people = v.findViewById(R.id.post_people);
            level = v.findViewById(R.id.post_level);
            time = v.findViewById(R.id.post_time);
        }
    }
}
