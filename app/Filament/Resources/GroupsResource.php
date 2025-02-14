<?php

namespace App\Filament\Resources;

use App\Filament\Resources\GroupsResource\Pages;
use App\Filament\Resources\GroupsResource\RelationManagers;
use App\Models\Groups;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\SoftDeletingScope;

class GroupsResource extends Resource
{
    protected static ?string $model = Groups::class;
    protected static ?string $navigationGroup = 'Menu';
    protected static ?string $navigationIcon = 'heroicon-o-rectangle-group';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                //
                Forms\Components\TextInput::make('menugrouptext')
                ->required()
                ->maxLength(15),
                Forms\Components\Toggle::make('menugroupinactive')
                ->required()
                ->inline(false),
                Forms\Components\TextInput::make('menugroupid')
                ->required()
                ->numeric()
                ->minValue(1)
                ->maxValue(100),
                Forms\Components\TextInput::make('displayindex')
                ->required()
                ->numeric()
                ->minValue(-1)
                ->maxValue(31),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                //
                Tables\Columns\TextColumn::make('menugroupid'),
                Tables\Columns\TextColumn::make('menugrouptext')
                ->searchable(),
                Tables\Columns\CheckboxColumn::make('menugroupinactive')
                ->disabled()
            ])
            ->filters([
                //
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                ]),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListGroups::route('/'),
            'create' => Pages\CreateGroups::route('/create'),
            'edit' => Pages\EditGroups::route('/{record}/edit'),
        ];
    }
}
