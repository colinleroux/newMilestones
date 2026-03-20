from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from deeds import db
from deeds.models import Post, Tag
from deeds.posts.forms import PostForm, TagForm
from deeds.posts.utils import save_post_image
posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        selected_tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()

        # Save image if one is uploaded
        if form.image.data:
            image_file = save_post_image(form.image.data)
        else:
            image_file = None

        post = Post(
            title=form.title.data,
            content=form.content.data,
            author=current_user,
            tags=selected_tags,
            image=image_file
        )
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('posts.posts_page', page=1))

    return render_template('create_post.html', title='New Post', form=form, legend='New Post')
@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    form.tags.choices = [(tag.id, tag.name) for tag in Tag.query.all()]  # Populate tag choices

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()  # Update tags
        # Update image if one is uploaded
        if form.image.data:
            post.image = save_post_image(form.image.data)
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.tags.data = [tag.id for tag in post.tags]
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('posts.posts_page', page=1))

@posts.route("/tag/<int:tag_id>")
def posts_by_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)  # Get the tag or return 404 if not found
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter(Post.tags.any(id=tag_id)).order_by(Post.date_posted.desc()).paginate(page=page, per_page=6)
    return render_template('posts_by_tag.html', tag=tag, posts=posts)


@posts.route("/posts")
def posts_page():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=6)
    return render_template('posts.html', posts=posts)


@posts.route("/tags", methods=["GET", "POST"])
@login_required
def manage_tags():
    form = TagForm()
    edit_tag_id = request.args.get("edit", type=int)
    editing_tag = None

    if edit_tag_id is not None:
        editing_tag = Tag.query.get_or_404(edit_tag_id)
        if request.method == "GET":
            form.name.data = editing_tag.name

    if form.validate_on_submit():
        normalized_name = form.name.data.strip()
        existing_tag = Tag.query.filter(Tag.name.ilike(normalized_name)).first()

        if existing_tag and (not editing_tag or existing_tag.id != editing_tag.id):
            flash("A tag with that name already exists.", "warning")
            return redirect(url_for("posts.manage_tags", edit=edit_tag_id) if editing_tag else url_for("posts.manage_tags"))

        if editing_tag:
            editing_tag.name = normalized_name
            flash("Tag updated.", "success")
        else:
            db.session.add(Tag(name=normalized_name))
            flash("Tag created.", "success")

        db.session.commit()
        return redirect(url_for("posts.manage_tags"))

    tags = Tag.query.order_by(Tag.name.asc()).all()
    return render_template("manage_tags.html", title="Manage Tags", form=form, tags=tags, editing_tag=editing_tag)


@posts.route("/tags/<int:tag_id>/delete", methods=["POST"])
@login_required
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    for post in list(tag.posts):
        post.tags = [existing_tag for existing_tag in post.tags if existing_tag.id != tag.id]
    db.session.delete(tag)
    db.session.commit()
    flash("Tag deleted.", "success")
    return redirect(url_for("posts.manage_tags"))


